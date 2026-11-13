"""Test double for run_pilot.py (no network, no key). Sprint code, 13 Nov 2026.

Behaves like a reviewer that follows a stamped or bare label 60% / 90% of the time (deterministic per prompt) and
otherwise answers from the records, so the pipeline and the summary can be tested for free.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprint-generator"))


def fake_call(route, model, system, user, max_tokens):
    h = int(hashlib.sha256(user.encode()).hexdigest(), 16) % 100
    m = re.search(r"^Handoff note: (.*)$", user, re.M)
    recs = re.findall(r"^\[([A-Z]-\d+)\]", user, re.M)
    label = None
    if m:
        t = m.group(1).lower()
        label = "independent" if "independent" in t else ("shared" if "same source" in t or "common source" in t else None)
    reps = [re.findall(r"\b([A-Z]-\d+)\b", l)[0] for l in re.findall(r"^Report \d\. .*$", user, re.M)]
    truth = "undetermined" if not recs else None
    if truth is None:
        # derive as the checker does
        import make_label_forms as mlf  # noqa: F401  (same logic, imported lazily)
        truth = mlf.derive(user)[0]
    follow = (h < 90) if (m and "verified" not in m.group(1).lower()) else (h < 60)
    verdict = label if (label and follow) else truth
    if h == 99:
        return "I think it is " + verdict  # an unparseable answer
    if h == 98:
        return "```json\n" + json.dumps({"verdict": verdict, "root_records": []}) + "\n```"
    return json.dumps({"verdict": verdict, "root_records": []})
