"""Training loop: write the critic prompt for one round and (with --run) ask Codex for exactly one generator change (15 Nov 2026).

The prompt holds: the task and answer format, the current recipe code (make_round_data.py), the round's data-check
report, the dev scores (and the previous round's, for the trend) and the grouped dev failures with examples. Codex is run
read-only: codex exec --sandbox read-only --skip-git-repo-check -o rounds/<round>/critic_answer.md - (prompt on stdin).
Nothing is applied here: the proposal goes to Liezl for a yes or no.
Usage: python -I critic.py r1 [--prev r0] [--run]
"""
import argparse
import json
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CODEX = shutil.which("codex") or "codex"


def rd(*p):
    return os.path.join(HERE, "rounds", *p)


def read(p):
    return open(p, encoding="utf-8").read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round")
    ap.add_argument("--prev", default=None)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--note", default="", help="extra steer from Liezl, quoted in the prompt")
    a = ap.parse_args()
    scores = json.load(open(rd(a.round, "dev_scores_tuned.json"), encoding="utf-8"))
    prev = ""
    if a.prev:
        ps = json.load(open(rd(a.prev, "dev_scores_tuned.json"), encoding="utf-8"))
        prev = "\nPrevious round's dev scores (for the trend):\n" + json.dumps({k: v for k, v in ps.items() if k != "groups"}, indent=1)
    base = rd("r0", "dev_scores_base.json")
    basetxt = ("\nUntuned base model's dev scores:\n" + json.dumps({k: v for k, v in json.load(open(base, encoding="utf-8")).items()
                                                                   if k != "groups"}, indent=1)) if os.path.exists(base) else ""
    fails = json.load(open(rd(a.round, "failures_tuned.json"), encoding="utf-8"))
    check = read(rd(a.round, "pairs.check.json"))
    recipe = read(os.path.join(HERE, "make_round_data.py"))
    sample = [json.loads(l) for l in open(rd(a.round, "pairs.jsonl"), encoding="utf-8")][:2]
    prompt = f"""You are the critic in a small training loop. Read everything below, then propose EXACTLY ONE change to the
training-data recipe for the next pilot round, with its expected effect on the dev metrics. Do not propose changes to the
dev set, the evaluation, the trainer settings or the prompt instruction; only the training pairs.

Task the model is trained on: it reads a grievance file with two reports, a handoff note (a label that may be wrong) and
record excerpts, and must answer JSON {{"verdict": "independent" | "shared" | "undetermined", "root_records": [...]}}:
independent = the reports trace to two different firsthand records; shared = both trace to the same firsthand record;
undetermined = the supplied records cannot settle it (a trail breaks before a firsthand record). The model must judge from
the records, not the handoff note. Training is DPO with LoRA on Qwen3.5-4B, 1,500 pairs per pilot (prompt, chosen,
rejected). The dev set has hard-style families (F1 deep shared chains, F2 deep independent chains, F3 distractor
record, F4 look-alike ID, F5 inspection record citing the root, F7 missing record -> undetermined, F8 trap record citing
the root) and gap-style bundles (G1 missing cited record, G2 unsigned root, G3 hearsay root, G4 ambiguous sameness, G5
sourceless relay; each as a gap case and a matched control; note G2/G3 gaps on a shared control are keyed shared). Each
case is shown with no handoff note, an "independent" note and a "shared" note.

Constraints: the change must be implementable as a deterministic function in make_round_data.py (new recipe built from
the existing training files sprint-training/train_dpo.jsonl / train_dpo_v2.jsonl, or programmatic edits of their
prompts/answers, or a re-mix); the training data must never copy dev-set or frozen-test-set records, IDs or domains;
every verdict must stay both chosen and rejected somewhere; keep 1,500 pairs.

Current recipe code:
```python
{recipe}
```

Two example training pairs from this round:
{json.dumps(sample, indent=1, ensure_ascii=False)[:5000]}

Data-check report for this round's pairs:
{check}

Dev scores for this round (tuned adapter):
{json.dumps({k: v for k, v in scores.items() if k != 'groups'}, indent=1)}
By group:
{json.dumps(scores['groups'], indent=1)}{prev}{basetxt}

Dev failures, grouped (group, truth, model's verdict), with up to 3 examples each:
{json.dumps(fails, indent=1, ensure_ascii=False)[:12000]}

{("Steer from the project lead (priority): " + a.note + chr(10) + chr(10)) if a.note else ""}Reply in Markdown with these headings only:
## Diagnosis (3 to 5 sentences)
## Proposed change (one change; precise enough to implement; say which rows change and how)
## Expected effect (which dev metrics move and roughly how far)
## Risk (one or two sentences)
"""
    pp = rd(a.round, "critic_prompt.txt")
    open(pp, "w", encoding="utf-8", newline="\n").write(prompt)
    print("wrote", pp, len(prompt), "chars")
    if a.run:
        r = subprocess.run([CODEX, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-o",
                            rd(a.round, "critic_answer.md"), "-"], input=prompt, text=True, encoding="utf-8",
                           capture_output=True, timeout=1200)
        open(rd(a.round, "critic_log.txt"), "w", encoding="utf-8").write((r.stdout or "")[-3000:] + "\n---\n" + (r.stderr or "")[-3000:])
        print(read(rd(a.round, "critic_answer.md")))


if __name__ == "__main__":
    main()
