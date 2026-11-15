"""Training loop: data checks run before every pilot; exit 1 (block) if any blocking check fails (15 Nov 2026).

Checks on a DPO pairs file (prompt, chosen, rejected):
  1. counts of chosen and rejected answers by verdict;
  2. BLOCK if a verdict is never rejected or never chosen;
  3. handoff label against truth (chosen verdict), as a cross-table;
  4. BLOCK on exact duplicate prompts or any pair whose chosen equals rejected; near duplicates (prompt with every
     record ID and clock time masked) reported, blocking only above 5%;
  5. overlap with the frozen sets (main 15 variants, hard set, gap set) and the dev set: BLOCK on any shared record ID
     or any shared record text / packet; frozen and dev domain names found in training prompts are reported (blocking
     for the dev and frozen-set domain lists);
  6. prompt-length spread (characters): min, p10, median, p90, max.
Writes <pairs>.check.json beside the pairs file and prints a short summary.
Usage: python -I check_data.py rounds/r0/pairs.jsonl
"""
import collections
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SR = os.path.join(REPO, "sprint-code", "scored-run")
FROZEN = {
    "main15": os.path.join(REPO, "variants", "joined-15", "packets_scored.jsonl"),
    "hard": os.path.join(SR, "hard-set", "packets_hard.jsonl"),
    "gap": os.path.join(SR, "gap-set", "packets_gap.jsonl"),
    "dev": os.path.join(HERE, "dev", "packets_dev.jsonl"),
}
DOMAINS = {
    "hard": ["port customs", "hotel kitchen", "lab freezer", "bus depot", "pharmacy", "bank branch", "farm co-op",
             "call centre"],
    "gap": ["ferry terminal", "fire station", "museum archive", "brewery", "recycling plant", "dental clinic",
            "observatory", "vineyard"],
    "dev": ["airport cargo shed", "school canteen", "water utility", "ski lodge", "shipyard", "printing works", "zoo",
            "textile mill"],
}
VERDICTS = ("independent", "shared", "undetermined")
ID_RE = re.compile(r"\b[A-Z]{1,2}-\d{2,5}\b")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\b")


def verdict(ans):
    try:
        return json.loads(ans)["verdict"]
    except Exception:  # noqa: BLE001
        return "UNPARSEABLE"


def label_of(prompt):
    m = re.search(r"Handoff note: (.*)", prompt)
    if not m:
        return "none"
    t = m.group(1).lower()
    if "independen" in t:
        return "independent"
    if "same source" in t or "common source" in t or "repeat" in t:
        return "shared"
    return "other"


def records_part(prompt):
    i = prompt.find("Record")
    return prompt[i:] if i >= 0 else prompt


def record_lines(prompt):
    return {l.strip() for l in records_part(prompt).splitlines() if ID_RE.match(l.strip().lstrip("["))}


def strip_ids(line):
    return ID_RE.sub("#", line)


def main():
    path = sys.argv[1] if os.path.isabs(sys.argv[1]) else os.path.join(HERE, sys.argv[1])
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    rep, block = {"file": os.path.relpath(path, HERE).replace("\\", "/"), "n": len(rows)}, []

    ch = collections.Counter(verdict(r["chosen"]) for r in rows)
    rj = collections.Counter(verdict(r["rejected"]) for r in rows)
    rep["chosen_by_verdict"], rep["rejected_by_verdict"] = dict(ch), dict(rj)
    pairs = collections.Counter(f"{verdict(r['chosen'])}>{verdict(r['rejected'])}" for r in rows)
    rep["chosen_over_rejected"] = dict(pairs.most_common())
    for v in VERDICTS:
        if ch[v] == 0:
            block.append(f"verdict '{v}' is never chosen")
        if rj[v] == 0:
            block.append(f"verdict '{v}' is never rejected")
    if ch["UNPARSEABLE"] or rj["UNPARSEABLE"]:
        block.append("unparseable chosen or rejected answers")

    xt = collections.defaultdict(collections.Counter)
    for r in rows:
        xt[label_of(r["prompt"])][verdict(r["chosen"])] += 1
    rep["label_by_truth"] = {k: dict(v) for k, v in sorted(xt.items())}

    prompts = [r["prompt"] for r in rows]
    dup = len(prompts) - len(set(prompts))
    same = sum(r["chosen"] == r["rejected"] for r in rows)
    near = len(prompts) - len({TIME_RE.sub("#", strip_ids(p)) for p in prompts})
    rep["duplicates"] = {"exact_prompt": dup, "chosen_equals_rejected": same, "near_prompt_ids_times_masked": near,
                         "near_rate": round(near / max(1, len(rows)), 4)}
    if dup:
        block.append(f"{dup} exact duplicate prompts")
    if same:
        block.append(f"{same} pairs with chosen == rejected")
    if near / max(1, len(rows)) > 0.05:
        block.append(f"near-duplicate rate {near / len(rows):.1%} > 5%")

    train_ids = set(ID_RE.findall("\n".join(records_part(p) for p in prompts)))
    train_lines = set().union(*(record_lines(p) for p in prompts)) if prompts else set()
    train_lines_noid = {strip_ids(l) for l in train_lines}
    low = "\n".join(prompts).lower()
    ov = {}
    for name, fp in FROZEN.items():
        if not os.path.exists(fp):
            ov[name] = "MISSING FILE"
            block.append(f"frozen/dev file missing: {name}")
            continue
        fr = [json.loads(l)["prompt"] for l in open(fp, encoding="utf-8") if l.strip()]
        ids = set(ID_RE.findall("\n".join(records_part(p) for p in fr)))
        flines = set().union(*(record_lines(p) for p in fr))
        shared_ids = sorted(ids & train_ids)
        shared_text = sorted({strip_ids(l) for l in flines} & train_lines_noid)
        packets = len({p.split("\n\n", 1)[-1] for p in fr} & {p.split("\n\n", 1)[-1] for p in prompts})
        doms = sorted(d for d in DOMAINS.get(name, []) if d in low)
        ov[name] = {"shared_record_ids": shared_ids[:20], "n_shared_record_ids": len(shared_ids),
                    "shared_record_texts_ids_masked": len(shared_text), "shared_packets": packets, "domains_in_train": doms}
        if shared_ids or shared_text or packets:
            block.append(f"overlap with {name}: ids {len(shared_ids)}, texts {len(shared_text)}, packets {packets}")
        if doms:
            block.append(f"{name} domains appear in training prompts: {doms}")
    rep["overlap"] = ov

    L = sorted(len(p) for p in prompts)
    q = statistics.quantiles(L, n=10) if len(L) > 1 else [L[0]] * 9
    rep["prompt_chars"] = {"min": L[0], "p10": int(q[0]), "median": int(statistics.median(L)), "p90": int(q[8]),
                           "max": L[-1]}
    rep["blocking_failures"] = block
    rep["pass"] = not block
    out = path.replace(".jsonl", ".check.json")
    json.dump(rep, open(out, "w", encoding="utf-8", newline="\n"), indent=1)
    print(json.dumps({k: rep[k] for k in ("n", "chosen_by_verdict", "rejected_by_verdict", "duplicates", "prompt_chars",
                                           "blocking_failures", "pass")}, indent=1))
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
