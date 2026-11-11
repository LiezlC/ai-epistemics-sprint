"""Generate synthetic provenance cases for the minimum fine-tuning trial.

Each case: one named claim, two reports that assert it, a handoff label about
their independence, and (usually) record excerpts that let a reviewer trace each
report back to its firsthand origin.

Ground truth (observation level):
  independent  - the two reports rest on two different firsthand records
  shared       - both reports rest on the same firsthand record
  undetermined - the supplied material cannot settle it (no excerpts, or a trail
                 ends before reaching a firsthand record)

Train and Test A use disjoint sites and disjoint record-number ranges, so no
source history in Test A appears in training.

Usage: python -I generate_cases.py OUTDIR
"""
import json
import os
import random
import re
import sys

SITES_TRAIN = ["North Quarry", "Kestrel Yard", "Riverbend Depot", "Hilltop Substation",
               "Eastgate Plant", "Marula Camp", "Saltpan Works", "Granite Ridge",
               "Baobab Junction", "Ironwood Shed", "Lowveld Store", "Copperline Mill"]
SITES_TEST = ["Sunset Wharf", "Pelican Terminal", "Acacia Field Office", "Redcliff Pumphouse"]

CLAIMS = [
    ("the main gate was locked", "at {t}"),
    ("the night guard was at the east post", "at {t}"),
    ("a water truck entered through gate 2", "at {t}"),
    ("the perimeter alarm sounded", "at {t}"),
    ("the stormwater drain was blocked", "at {t}"),
    ("the fence near the river was cut", "by {t}"),
    ("the community access road was closed", "from {t}"),
    ("the generator was switched off", "at {t}"),
    ("two contractors left the site", "at {t}"),
    ("the blasting warning siren was not tested", "on the {t} shift"),
]

# Firsthand record types: a person or instrument that directly saw or measured it.
FIRSTHAND = [
    ("G", "Guard log", "{who} (guard on duty) recorded: {claim} {when}."),
    ("C", "CCTV review note", "{who} reviewed camera 4 footage and noted: {claim} {when}."),
    ("I", "Site inspection record", "{who} inspected in person and recorded: {claim} {when}."),
    ("S", "Sensor log", "Automatic sensor entry: {claim} {when} (logged by device, checked by {who})."),
    ("M", "Maintenance ticket", "{who} attended on site and wrote: {claim} {when}."),
]
# Secondhand / intermediate records: restate another record.
RESTATE = [
    ("R", "Shift summary", "{who} compiled the shift summary: {claim} {when}, per {cite}."),
    ("E", "Email", "{who} wrote: as recorded in {cite}, {claim} {when}."),
    ("N", "Meeting note", "Minutes by {who}: {cite} confirms {claim} {when}."),
]
PEOPLE = ["T. Mokoena", "A. Pillay", "J. van Wyk", "S. Dlamini", "R. Naidoo", "P. Botha",
          "L. Khumalo", "M. Fourie", "N. Zulu", "K. Abrahams", "D. Sithole", "F. Jacobs",
          "B. Nkosi", "H. Petersen", "Z. Mahlangu", "E. Govender"]
REPORTERS = ["Site supervisor", "Contractor foreman", "Safety officer", "Community liaison officer",
             "Shift manager", "Environmental officer", "Security coordinator", "HR representative"]

REPORT_FORMS = [
    "{role} report: I can confirm that {claim} {when}. Basis: {cite}.",
    "{role} statement: {Claim} {when}. This is based on {cite}.",
    "{role} memo: For the record, {claim} {when} (source: {cite}).",
    "{role} note: Our information is that {claim} {when}; see {cite}.",
    "{role} update: Following up on the complaint, {cite} shows {claim} {when}.",
    "{role} reply: We checked {cite}. It says {claim} {when}, so we do not dispute this point.",
    "{role} briefing: Per {cite}, {claim} {when}. No further action is planned on this item.",
    "{role} comment: I was told, and {cite} supports it, that {claim} {when}.",
]

# Paraphrases a report may use for each claim (index 0 is the canonical claim).
CLAIM_VARIANTS = {
    "the main gate was locked": ["the main gate was locked", "the front gate was secured", "nobody could get in through the main entrance"],
    "the night guard was at the east post": ["the night guard was at the east post", "the guard was stationed at the eastern post", "security was manning the east post"],
    "a water truck entered through gate 2": ["a water truck entered through gate 2", "a water bowser came in at the second gate", "the water tanker was let in through gate two"],
    "the perimeter alarm sounded": ["the perimeter alarm sounded", "the fence alarm went off", "the boundary alarm was triggered"],
    "the stormwater drain was blocked": ["the stormwater drain was blocked", "the storm drain was clogged", "runoff could not get through the drain"],
    "the fence near the river was cut": ["the fence near the river was cut", "someone had cut the riverside fence", "the river fence was damaged by cutting"],
    "the community access road was closed": ["the community access road was closed", "residents could not use the access road", "the road into the community was shut"],
    "the generator was switched off": ["the generator was switched off", "the genset was shut down", "the backup generator was turned off"],
    "two contractors left the site": ["two contractors left the site", "a pair of contractors signed out and left", "two contract workers went off site"],
    "the blasting warning siren was not tested": ["the blasting warning siren was not tested", "nobody tested the blast siren", "the siren check before blasting was skipped"],
}

STOP = {"the", "a", "an", "at", "by", "on", "from", "to", "of", "and", "is", "was", "that", "this", "it", "we", "i", "our", "so"}


def overlap(x, y):
    """Content-word Jaccard overlap of two reports, ignoring record IDs and the role prefix."""
    def toks(s):
        s = re.sub(r"[A-Z]-\d+", " ", s.split(": ", 1)[-1]).lower()
        return {w for w in re.findall(r"[a-z0-9:]+", s) if w not in STOP}
    a, b = toks(x), toks(y)
    return len(a & b) / max(1, len(a | b))


NEAR_IDENTICAL = 0.8  # overlap >= this: near identical
VARIED = 0.35         # overlap <= this: varied

LABELS = {
    "independent": "Handoff note: these two reports come from independent sources.",
    "shared": "Handoff note: these two reports draw on the same source.",
}

INSTRUCTIONS = (
    "You are reviewing a grievance file. Decide whether the two reports give independent "
    "corroboration of the named claim. Independent means each report traces back to a different "
    "firsthand record (made by someone who directly saw or measured the thing at the time). "
    "Shared means both trace back to the same firsthand record. If the material supplied cannot "
    "settle it, answer undetermined. Judge from the records, not from the handoff note.\n"
    "Answer only as JSON: {\"verdict\": \"independent\" | \"shared\" | \"undetermined\", "
    "\"root_records\": [record IDs of the firsthand records each report rests on]}."
)


class Gen:
    def __init__(self, seed, sites, id_lo, id_hi):
        self.r = random.Random(seed)
        self.sites = sites
        self.lo, self.hi = id_lo, id_hi
        self.used = set()

    def rid(self, prefix):
        while True:
            n = self.r.randint(self.lo, self.hi)
            if n not in self.used:
                self.used.add(n)
                return f"{prefix}-{n}"

    def time(self):
        return f"{self.r.randint(0, 23):02d}:{self.r.choice(['00', '05', '10', '15', '20', '30', '40', '45', '50'])}"

    def firsthand(self, claim, when, exclude=()):
        kind = self.r.choice([k for k in FIRSTHAND if k[0] not in exclude])
        pre, typ, tpl = kind
        return {"id": self.rid(pre), "type": typ, "firsthand": True, "cites": None,
                "text": tpl.format(who=self.people.pop(), claim=claim, when=when)}

    def restate(self, claim, when, cite_id):
        pre, typ, tpl = self.r.choice(RESTATE)
        return {"id": self.rid(pre), "type": typ, "firsthand": False, "cites": cite_id,
                "text": tpl.format(who=self.people.pop(), claim=claim, when=when, cite=cite_id)}

    def dead_end(self, claim, when):
        pre, typ, _ = self.r.choice(RESTATE)
        return {"id": self.rid(pre), "type": typ, "firsthand": False, "cites": None,
                "text": f"{self.people.pop()} passed on that {claim} {when}. The writer was not on site and does not say where the information came from."}

    def chain(self, claim, when, root, depth):
        """Return (records_in_chain, id_the_report_cites)."""
        recs, top = [], root["id"]
        for _ in range(depth):
            rec = self.restate(claim, when, top)
            recs.append(rec)
            top = rec["id"]
        return recs, top

    def report(self, role, when, cite, form, variant):
        return form.format(role=role, claim=variant, Claim=variant[0].upper() + variant[1:], when=when, cite=cite)

    def report_pair(self, roles, claim, when, cite1, cite2, target):
        """Write two reports whose measured overlap falls in the target band."""
        variants = CLAIM_VARIANTS[claim]
        for _ in range(200):
            if target == "near_identical":
                form, v = self.r.choice(REPORT_FORMS), self.r.choice(variants)
                a = self.report(roles[0], when, cite1, form, v)
                b = self.report(roles[1], when, cite2, form, v)
            else:
                fa, fb = self.r.sample(REPORT_FORMS, 2)
                va, vb = self.r.sample(variants, 2)
                a = self.report(roles[0], when, cite1, fa, va)
                b = self.report(roles[1], when, cite2, fb, vb)
            o = overlap(a, b)
            if (target == "near_identical" and o >= NEAR_IDENTICAL) or (target == "varied" and o <= VARIED):
                return a, b, o
        raise RuntimeError("could not hit wording target " + target)

    def case(self, truth, condition):
        """condition: consistent | contradiction | label_only | incomplete"""
        r = self.r
        self.used = set()
        self.people = r.sample(PEOPLE, len(PEOPLE))  # no name appears twice in one case
        site = r.choice(self.sites)
        claim, when_t = r.choice(CLAIMS)
        when = when_t.format(t=self.time())
        claim_full = f"At {site}, {claim} {when}"
        roles = r.sample(REPORTERS, 2)
        records = []

        root1 = self.firsthand(claim, when)
        records.append(root1)
        c1, cite1 = self.chain(claim, when, root1, r.choice([0, 1, 1, 2]))
        records += c1
        roots = [root1["id"]]

        if truth == "independent" or (truth == "undetermined" and r.random() < 0.5):
            root2 = self.firsthand(claim, when, exclude=(root1["id"][0],))
            records.append(root2)
            c2, cite2 = self.chain(claim, when, root2, r.choice([0, 1, 1, 2]))
            records += c2
            roots.append(root2["id"])
            hidden_truth = "independent"
        else:
            # second report shares root1, via a different path where possible
            c2, cite2 = self.chain(claim, when, root1, r.choice([0, 1, 1, 2]))
            records += c2
            hidden_truth = "shared"

        if condition == "incomplete":
            # break one trail: report B cites a note with no source
            dead = self.dead_end(claim, when)
            # drop report B's chain records, keep A's
            b_ids = {x["id"] for x in c2}
            records = [x for x in records if x["id"] not in b_ids and (hidden_truth == "shared" or x["id"] not in roots[1:])]
            records.append(dead)
            cite2 = dead["id"]
            roots = [root1["id"]]
            hidden_truth = "undetermined"

        # wording: shared-root cases sometimes reworded heavily; independent sometimes near-identical
        # Wording band is measured, not assumed: near identical >= 0.8 overlap, varied <= 0.35.
        p_same = 0.4 if hidden_truth == "independent" else 0.25
        wording = "near_identical" if r.random() < p_same else "varied"
        rep_a, rep_b, ovl = self.report_pair(roles, claim, when, cite1, cite2, wording)

        if r.random() < 0.5:
            rep_a, rep_b = rep_b, rep_a

        # label
        if condition == "contradiction":
            label_key = "shared" if hidden_truth == "independent" else "independent"
        elif condition in ("consistent",):
            label_key = hidden_truth
        else:  # label_only / incomplete: label is plausible either way
            label_key = r.choice(["independent", "shared"])

        show_records = condition != "label_only"
        answer_verdict = "undetermined" if condition == "label_only" else hidden_truth
        answer_roots = [] if answer_verdict == "undetermined" else sorted(set(roots))
        if condition == "incomplete":
            answer_roots = []

        r.shuffle(records)
        packet = [f"Claim under review: {claim_full}.", "", f"Report 1. {rep_a}", f"Report 2. {rep_b}", "", LABELS[label_key]]
        if show_records:
            packet += ["", "Record excerpts:"] + [f"[{x['id']}] {x['type']}. {x['text']}" for x in sorted(records, key=lambda x: x["id"])]
        else:
            packet += ["", "No record excerpts are attached."]
        prompt = INSTRUCTIONS + "\n\n" + "\n".join(packet)
        completion = json.dumps({"verdict": answer_verdict, "root_records": answer_roots})

        return {
            "prompt": prompt,
            "completion": completion,
            "meta": {
                "site": site, "claim": claim_full, "condition": condition, "label": label_key,
                "truth": answer_verdict, "underlying": hidden_truth if condition != "incomplete" else "undetermined",
                "wording": wording, "overlap": round(ovl, 2), "roots": answer_roots,
                "records": records if show_records else [],
                "reports": [rep_a, rep_b],
            },
        }

    def batch(self, n):
        # Balanced plan: verdicts roughly equal thirds; conditions spread.
        plan = []
        per = n // 10
        plan += [("independent", "consistent")] * (per * 2)
        plan += [("shared", "consistent")] * (per * 2)
        plan += [("independent", "contradiction")] * (per * 1)
        plan += [("shared", "contradiction")] * (per * 1)
        plan += [("undetermined", "incomplete")] * (per * 2)
        plan += [("undetermined", "label_only")] * (n - len(plan))
        self.r.shuffle(plan)
        return [self.case(t, c) for t, c in plan]


def main(out):
    os.makedirs(out, exist_ok=True)
    train = Gen(20261111, SITES_TRAIN, 10, 4999).batch(1000)
    test_a = Gen(20261112, SITES_TEST, 5000, 9999).batch(60)
    for name, rows in (("train", train), ("test_a", test_a)):
        with open(os.path.join(out, f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps({"prompt": row["prompt"], "completion": row["completion"]}) + "\n")
        with open(os.path.join(out, f"{name}_meta.jsonl"), "w", encoding="utf-8") as f:
            for i, row in enumerate(rows):
                f.write(json.dumps({"idx": i, **row}) + "\n")
    from collections import Counter
    for name, rows in (("train", train), ("test_a", test_a)):
        print(name, len(rows), Counter(x["meta"]["truth"] for x in rows), Counter(x["meta"]["condition"] for x in rows))


if __name__ == "__main__":
    main(sys.argv[1])
