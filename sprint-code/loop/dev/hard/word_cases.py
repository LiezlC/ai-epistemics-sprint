"""Hard set, step 2 and 3: Codex writes the wording for each skeleton; the checker gates it (15 Nov 2026).

Codex (codex exec --sandbox read-only --skip-git-repo-check -, prompt on stdin, answer via -o) returns JSON only:
{"claim", "report1", "report2", "records": {ID: {"type", "text"}}}. This script assembles the packet in the main-15
layout, so the "(see X)" tails, the record order and the handoff line come from the skeleton, never from Codex.
Then check_cases.check runs. A failing case is reworded once (Codex is told what failed); if it fails again it is dropped.
Outputs: codex/<case>.try<n>.prompt.txt and .answer.txt, cases.jsonl (passing cases), dropped.json.
The stored packet carries the "independent" label; make_packets.py writes both label versions.
Usage: python -I word_cases.py [--workers 6] [--only h000,h001]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_cases  # noqa: E402

LABEL_IND = "These two reports are independent."
CODEX = shutil.which("codex") or "codex"

ROLE_TEXT = {
    "root": "FIRSTHAND ROOT. In its own words, a named person (observer {obs}) directly saw, measured or recorded the claimed event at the event time. It names NO other record ID.",
    "relay": "RELAY. Made by someone who did not see the event. Says in plain words that its information is taken from record {cites} (name that ID exactly). Names no other ID.",
    "inspection": "LATE INSPECTION. Written by an inspector at a time clearly LATER than the event. Says explicitly that its information about the event comes from record {cites} (name that ID exactly). Must not claim the inspector saw the event. Names no other ID.",
    "trap": "WORDING TRAP. A relay that uses the word \"independently\" (e.g. \"independently confirmed\") but in fact says its information is taken from record {cites} (name that ID exactly). Names no other ID.",
    "distractor": "UNCITED DISTRACTOR. Looks firsthand: a named person (observer {obs}) directly saw or measured something about the same event at the time. No report and no record cites it. Names NO other record ID.",
    "lookalike": "LOOK-ALIKE. Looks firsthand: a named person (observer {obs}) directly saw or measured something about the same event at the time. Its ID is a near miss of {looks_like}; nothing cites it. Names NO other record ID.",
}


def prompt_for(sk, feedback=None):
    lines = []
    for r in sk["records"]:
        t = ROLE_TEXT[r["role"]].format(obs=r.get("observer", ""), cites=", ".join(r["cites"]),
                                        looks_like=r.get("looks_like", ""))
        lines.append(f"- {r['id']}: {t}")
    miss = ""
    if sk["missing"]:
        miss = (f"\nRecord {sk['missing'][0]} is cited but NOT supplied: do not write it. The record citing it must say "
                "plainly that its information is taken from it, so a reader cannot tell where that report's information "
                "ultimately came from.")
    style = ("The two reports state the claim in closely similar words." if sk["style"] == "close"
             else "The two reports state the claim in very different words (different phrasing, different time format).")
    fb = ""
    if feedback:
        fb = "\n\nA previous attempt failed these mechanical checks; fix them:\n- " + "\n- ".join(feedback)
    return f"""You write the wording for one short evidence-bundle test case. The structure is fixed; you only write text.
Setting: a {sk['domain']} (invented names and places only; no real organisations).

Write:
- claim: one specific checkable claim about a single event at a stated clock time (under 20 words).
- report1: a short report (under 25 words) stating the claim. Do NOT mention any record ID; the citation is added for you.
  Report 1 rests on record {sk['report1_cites']}.
- report2: same, resting on record {sk['report2_cites']}.
  {style}
- records: one entry per ID below, each with a short record "type" (2 to 4 words, e.g. "night shift log") and "text"
  (under 35 words, written as the record itself):
{chr(10).join(lines)}{miss}

Style: terse, realistic workplace records, varied between records, like these (different setting, do not reuse):
  supervisor shift summary: 06:45 Gate 3 locked. Taken from the guard's night log, entry G-52.
  guard night log: 06:45 Gate 3 padlocked and checked by hand. Initialled J. Marrow, gate guard.
Avoid boilerplate such as "I did not witness"; a relay simply says where its information came from.

Hard rules:
- Use every ID above exactly as spelled; invent no other IDs or codes of the form LETTERS-DIGITS anywhere.
- A record names another ID only where its role above says so.
- Different firsthand observers are different named people making different observations.
- Never use the words independent, independently, separate, separately, corroborate, "same source" except where a role says so.
- Names, times and places stay consistent across the case.
- Plain text: no double quotes inside any text, no line breaks.{fb}

Reply with ONLY a JSON object, no code fence:
{{"claim": "...", "report1": "...", "report2": "...", "records": {{"ID": {{"type": "...", "text": "..."}}}}}}"""


def assemble(sk, w):
    def rep(t, cid):
        t = t.strip().rstrip(".")
        return f"{t} (see {cid})."
    out = [f"Claim under review: {w['claim'].strip()}", "",
           f"Report 1. {rep(w['report1'], sk['report1_cites'])}",
           f"Report 2. {rep(w['report2'], sk['report2_cites'])}",
           f"Handoff note: {LABEL_IND}", "", "Records:"]
    for r in sk["records"]:
        x = w["records"].get(r["id"]) or {}
        out.append(f"{r['id']} ({str(x.get('type', '')).strip()}): \"{str(x.get('text', '')).strip()}\"")
    return "\n".join(out) + "\n"


def run_codex(case, n, prompt, d):
    base = os.path.join(d, f"{case}.try{n}")
    open(base + ".prompt.txt", "w", encoding="utf-8", newline="\n").write(prompt)
    try:
        r = subprocess.run([CODEX, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-o", base + ".answer.txt", "-"],
                           input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=600)
        open(base + ".log.txt", "w", encoding="utf-8").write((r.stdout or "")[-4000:] + "\n---\n" + (r.stderr or "")[-4000:])
        txt = open(base + ".answer.txt", encoding="utf-8").read().strip()
        txt = txt[txt.find("{"): txt.rfind("}") + 1]
        return json.loads(txt), None
    except Exception as e:  # noqa: BLE001
        return None, f"codex/parse error: {type(e).__name__}: {e}"


def do_case(sk, d):
    fb, hist = None, []
    for n in (1, 2):
        w, err = run_codex(sk["case"], n, prompt_for(sk, fb), d)
        if err:
            fails = [err]
        else:
            try:
                pk = assemble(sk, w)
                fails = check_cases.check(pk, sk)
            except Exception as e:  # noqa: BLE001
                fails = [f"assemble error: {e}"]
        hist.append({"try": n, "fails": fails})
        if not fails:
            return {"case": sk["case"], "family": sk["family"], "tries": n, "packet": pk, "wording": w}, hist
        fb = fails
    return None, hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    sks = json.load(open(os.path.join(HERE, "skeletons.json"), encoding="utf-8"))
    if a.only:
        keep = set(a.only.split(","))
        sks = [s for s in sks if s["case"] in keep]
    d = os.path.join(HERE, "codex")
    os.makedirs(d, exist_ok=True)
    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda s: (s, do_case(s, d)), sks))
    ok = [r for _, (r, _) in res if r]
    dropped = {s["case"]: {"family": s["family"], "history": h} for s, (r, h) in res if not r}
    log = {s["case"]: h for s, (r, h) in res}
    suffix = "" if not a.only else ".partial"
    with open(os.path.join(HERE, f"cases{suffix}.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in ok:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(dropped, open(os.path.join(HERE, f"dropped{suffix}.json"), "w", encoding="utf-8"), indent=1)
    json.dump(log, open(os.path.join(HERE, f"check_log{suffix}.json"), "w", encoding="utf-8"), indent=1)
    print(f"{len(ok)} passed, {len(dropped)} dropped")


if __name__ == "__main__":
    main()
