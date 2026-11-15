"""Gap set, steps 2 and 3: Codex writes the wording; the checker gates both versions (15 Nov 2026).
Adapted from hard-set/word_cases.py. One Codex call per bundle (codex exec --sandbox read-only --skip-git-repo-check
-o <file> -, prompt on stdin) returns JSON {"claim", "report1", "report2", "records": {ID: {"type", "text"}}, "gap_text"}.
This script assembles the CONTROL packet and the GAP packet from the same wording, so they are byte-identical except
the one gap record (G1: record M left out; G2 to G5: that record's text replaced by gap_text, same type). The "(see X)"
tails, record order and handoff line come from the skeleton. Both versions must pass check_cases.check; a failing bundle
is reworded once with the failures fed back, then dropped (both versions together).
Outputs: codex/<bundle>.try<n>.prompt.txt/.answer.txt, cases.jsonl (2 rows per passing bundle), dropped.json, check_log.json.
Stored packets carry the "independent" label; make_packets.py writes the three label conditions.
Usage: python -I word_cases.py [--workers 6] [--only g000,g001]
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

ROOT = ("FIRSTHAND ROOT. {obs} directly saw, measured or recorded the claimed event at the event time, in their own "
        "words, and the text names {obs} exactly as spelled. Names NO record ID and no other person from the list.")
RELAY = ("RELAY. Made by someone who did not see the event. Says in plain words that its information is taken from record "
         "{cites} (name that ID exactly). Names no other ID and none of the listed people.")

GAP = {
    "G2": ("gap_text: an alternative text for record {t} (same type) that states the same event details but gives NO maker, "
           "no person's name and no sign that anyone saw it firsthand (e.g. an unsigned note). Names no ID."),
    "G3": ("gap_text: an alternative text for record {t} (same type), still written by {obs} (name {obs} exactly), saying "
           "{obs} was told about the event by someone who is not named (use the word \"told\"). {obs} did not see it. "
           "Names no ID and no other listed person."),
    "G4": ("gap_text: an alternative text for record {t} (same type), written by {obs}, that also mentions {other} (name "
           "both exactly) and states the event details, but leaves it truly OPEN whether {obs} made a second, own "
           "observation or simply wrote down the same observation {other} made (for example: {obs}, with {other} on the "
           "06:45 round, gate found locked). Do not use the words told, heard, copied, relayed, passed on, according to, "
           "taken from. Names no ID."),
    "G5": ("gap_text: an alternative text for record {t} (same type) that states the event details and says the information "
           "was passed on (use the words \"passed on\") WITHOUT saying from whom or from which record. Names no ID and "
           "none of the listed people."),
}


def prompt_for(sk, feedback=None):
    lines = []
    for r in sk["records"]:
        t = ROOT.format(obs=r["observer"]) if r["role"] == "root" else RELAY.format(cites=", ".join(r["cites"]))
        lines.append(f"- {r['id']}: {t}")
    t = sk["target"]
    if sk["gap_type"] in GAP:
        tr = next(r for r in sk["records"] if r["id"] == t)
        obs = tr.get("observer", "")
        other = next((n for n in sk["names"] if n != obs), "")
        gap = "\n- " + GAP[sk["gap_type"]].format(t=t, obs=obs, other=other)
    else:
        gap = (f"\n- gap_text: write an empty string. (Record {t} will later be removed from one version, while the record "
               "citing it still names it; so write every record so it reads naturally either way.)")
    fb = ""
    if feedback:
        fb = "\n\nA previous attempt failed these mechanical checks; fix them:\n- " + "\n- ".join(feedback)
    return f"""You write the wording for one short evidence-bundle test case. The structure is fixed; you only write text.
Setting: a {sk['domain']} (invented names and places only; no real organisations).
Listed people: {', '.join(sk['names'])}. Use them only where a role says so; invent no other named people.

Write:
- claim: one specific checkable claim about a single event at a stated clock time (under 20 words).
- report1: a short report (under 25 words) stating the claim. Do NOT mention any record ID or listed person; the
  citation is added for you. Report 1 rests on record {sk['report1_cites']}.
- report2: same, resting on record {sk['report2_cites']}. The two reports use different wording.
- records: one entry per ID below, each with a short record "type" (2 to 4 words, e.g. "night shift log") and "text"
  (under 35 words, written as the record itself):
{chr(10).join(lines)}{gap}

Style: terse, realistic workplace records, varied between records, like these (different setting, do not reuse):
  supervisor shift summary: 06:45 Gate 3 locked. Taken from the guard's night log, entry G-52.
  guard night log: 06:45 Gate 3 padlocked and checked by hand. Initialled J. Marrow, gate guard.

Hard rules:
- Use every ID above exactly as spelled; invent no other IDs or codes of the form LETTERS-DIGITS anywhere.
- A record names another ID only where its role above says so.
- Firsthand roots must not use the words told, heard, passed on, according to, relayed, copied, taken from, reportedly.
- Never use the words independent, independently, separate, separately, corroborate, "same source".
- Names, times and places stay consistent across the case.
- Plain text: no double quotes inside any text, no line breaks.{fb}

Reply with ONLY a JSON object, no code fence:
{{"claim": "...", "report1": "...", "report2": "...", "records": {{"ID": {{"type": "...", "text": "..."}}}}, "gap_text": "..."}}"""


def assemble(sk, w, version):
    def rep(t, cid):
        return f"{t.strip().rstrip('.')} (see {cid})."
    out = [f"Claim under review: {w['claim'].strip()}", "",
           f"Report 1. {rep(w['report1'], sk['report1_cites'])}",
           f"Report 2. {rep(w['report2'], sk['report2_cites'])}",
           f"Handoff note: {LABEL_IND}", "", "Records:"]
    for r in sk["records"]:
        x = w["records"].get(r["id"]) or {}
        text = str(x.get("text", "")).strip()
        if version == "gap" and r["id"] == sk["target"]:
            if sk["gap_type"] == "G1":
                continue
            text = str(w.get("gap_text", "")).strip()
        out.append(f"{r['id']} ({str(x.get('type', '')).strip()}): \"{text}\"")
    return "\n".join(out) + "\n"


def run_codex(b, n, prompt, d):
    base = os.path.join(d, f"{b}.try{n}")
    open(base + ".prompt.txt", "w", encoding="utf-8", newline="\n").write(prompt)
    try:
        r = subprocess.run([CODEX, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-o", base + ".answer.txt", "-"],
                           input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=600)
        open(base + ".log.txt", "w", encoding="utf-8").write((r.stdout or "")[-4000:] + "\n---\n" + (r.stderr or "")[-4000:])
        txt = open(base + ".answer.txt", encoding="utf-8").read().strip()
        return json.loads(txt[txt.find("{"): txt.rfind("}") + 1]), None
    except Exception as e:  # noqa: BLE001
        return None, f"codex/parse error: {type(e).__name__}: {e}"


def do_bundle(sk, d):
    fb, hist = None, []
    for n in (1, 2):
        w, err = run_codex(sk["bundle"], n, prompt_for(sk, fb), d)
        pk = {}
        if err:
            fails = [err]
        else:
            try:
                fails = []
                for v in ("control", "gap"):
                    pk[v] = assemble(sk, w, v)
                    fails += check_cases.check(pk[v], sk, v)
            except Exception as e:  # noqa: BLE001
                fails = [f"assemble error: {e}"]
        hist.append({"try": n, "fails": fails})
        if not fails:
            rows = [{"case": sk["bundle"] + ("c" if v == "control" else ""), "bundle": sk["bundle"], "version": v,
                     "gap_type": sk["gap_type"], "tries": n, "packet": pk[v]} for v in ("gap", "control")]
            return rows, hist
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
        sks = [s for s in sks if s["bundle"] in keep]
    d = os.path.join(HERE, "codex")
    os.makedirs(d, exist_ok=True)
    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda s: (s, do_bundle(s, d)), sks))
    suffix = "" if not a.only else ".partial"
    n_ok = 0
    with open(os.path.join(HERE, f"cases{suffix}.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for s, (rows, h) in res:
            if rows:
                n_ok += 1
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
    dropped = {s["bundle"]: {"gap_type": s["gap_type"], "history": h} for s, (rows, h) in res if not rows}
    json.dump(dropped, open(os.path.join(HERE, f"dropped{suffix}.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    json.dump({s["bundle"]: h for s, (rows, h) in res},
              open(os.path.join(HERE, f"check_log{suffix}.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    print(f"{n_ok} bundles passed, {len(dropped)} dropped")


if __name__ == "__main__":
    main()
