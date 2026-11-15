"""Gap set: blind human-audit sheet (post-freeze, 15 Nov 2026). Writes gap-audit.html and audit_sample.json.

10 bundles drawn with seed 20261117 from the frozen cases: 5 shown as their gap version, 5 as their control version
(different bundles, so no matched pair appears). Each case shows the full packet with no handoff note. For each case the
auditor answers whether the records settle it and, if so, the verdict and the root records. The key is embedded encoded
and shown only after submit. Answers persist in localStorage (unique key) and export as gap-audit-answers.json.
Usage: python -I make_audit.py
"""
import base64
import html
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "sprint-code", "sprint-generator"))
import make_label_forms as m  # noqa: E402

SEED = 20261117
STORE = "gap-audit-answers-20261115-a7f3"


def main():
    cases = {json.loads(l)["case"]: json.loads(l) for l in open(os.path.join(HERE, "cases.jsonl"), encoding="utf-8") if l.strip()}
    key = json.load(open(os.path.join(HERE, "key.json"), encoding="utf-8"))
    bundles = sorted({c["bundle"] for c in cases.values()})
    rng = random.Random(SEED)
    pick = rng.sample(bundles, 10)
    chosen = [b for b in pick[:5]] + [b + "c" for b in pick[5:]]
    rng.shuffle(chosen)
    items, keyout = [], {}
    for i, c in enumerate(chosen, 1):
        pk = m.no_label(cases[c]["packet"]).rstrip("\n")
        ids = re.findall(r'^([A-Z]{1,4}-\d+) \(', pk, re.M)
        items.append({"n": i, "case": c, "packet": pk, "ids": ids})
        keyout[f"Q{i}"] = {"case": c, "version": key[c]["version"], "gap_type": key[c]["gap_type"],
                           "settled": key[c]["verdict"] != "undetermined", "verdict": key[c]["verdict"],
                           "root_records": key[c]["root_records"]}
    json.dump({"seed": SEED, "order": chosen, "key": keyout},
              open(os.path.join(HERE, "audit_sample.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    enc = base64.b64encode(json.dumps(keyout).encode()).decode()
    blocks = []
    for it in items:
        q = f"Q{it['n']}"
        roots = "".join(f'<label class="chip"><input type="checkbox" name="{q}-root" value="{i}"> {i}</label>' for i in it["ids"])
        blocks.append(f"""<section class="case" data-q="{q}">
<h2>Case {it['n']} <span class="tag">{it['case'][:4]}</span></h2>
<pre>{html.escape(it['packet'])}</pre>
<fieldset><legend>Do the records settle whether the two reports share a firsthand source?</legend>
<label><input type="radio" name="{q}-settled" value="yes"> Yes, the records settle it</label>
<label><input type="radio" name="{q}-settled" value="no"> No, they leave it open (undetermined)</label></fieldset>
<fieldset class="ifyes"><legend>If yes: verdict</legend>
<label><input type="radio" name="{q}-verdict" value="shared"> Shared root</label>
<label><input type="radio" name="{q}-verdict" value="independent"> Independent roots</label></fieldset>
<fieldset class="ifyes"><legend>If yes: tick the firsthand root record(s)</legend>{roots}</fieldset>
<label class="note">Note (optional) <input type="text" name="{q}-note"></label>
<div class="result"></div>
</section>""")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gap Set Audit</title><style>
:root{{--bg:#fafaf7;--fg:#1d1d1b;--mut:#666;--card:#fff;--line:#ddd;--ok:#1d7a3a;--bad:#b3261e;--acc:#2f5fb3}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161615;--fg:#eee;--mut:#aaa;--card:#202020;--line:#3a3a3a;--ok:#5fc27e;--bad:#ff8a80;--acc:#8fb2ff}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;margin:0;padding:16px;max-width:860px;margin-inline:auto}}
.case{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:18px 0}}
pre{{white-space:pre-wrap;word-wrap:break-word;font:14px/1.45 ui-monospace,Consolas,monospace;background:transparent;border-left:3px solid var(--line);padding-left:10px}}
fieldset{{border:none;padding:0;margin:10px 0}} legend{{font-weight:600;margin-bottom:4px}}
label{{display:block;margin:3px 0;cursor:pointer}} .chip{{display:inline-block;margin-right:14px}}
.tag{{display:none}} .note input{{width:100%;box-sizing:border-box;padding:6px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px}}
button{{font:inherit;padding:10px 18px;border-radius:8px;border:1px solid var(--acc);background:var(--acc);color:#fff;cursor:pointer;margin-right:10px}}
.result{{margin-top:8px;font-weight:600}} .ok{{color:var(--ok)}} .bad{{color:var(--bad)}} .mut{{color:var(--mut)}}
</style></head><body>
<h1>Gap set audit: 10 cases</h1>
<p class="mut">For each case, read the records and decide whether they settle where each report's information comes from. A firsthand root is a record whose named maker saw or measured the event. If any report's trail runs out (a missing record, no maker, hearsay, no source, or two records that may be one observation), choose "No". Your answers save in this browser. The key appears only after you press Submit.</p>
{''.join(blocks)}
<p><button id="submit">Submit and show key</button><button id="export">Download answers</button></p>
<p id="summary"></p>
<script>
const STORE="{STORE}",KEY=JSON.parse(atob("{enc}"));
function collect(){{const a={{}};document.querySelectorAll(".case").forEach(s=>{{const q=s.dataset.q;
const g=n=>{{const e=s.querySelector(`input[name="${{q}}-${{n}}"]:checked`);return e?e.value:null}};
a[q]={{settled:g("settled"),verdict:g("verdict"),roots:[...s.querySelectorAll(`input[name="${{q}}-root"]:checked`)].map(e=>e.value),note:s.querySelector(`input[name="${{q}}-note"]`).value}}}});return a}}
function save(){{try{{localStorage.setItem(STORE,JSON.stringify({{answers:collect(),submitted:window.SUB||false}}))}}catch(e){{}}}}
function restore(){{let d=null;try{{d=JSON.parse(localStorage.getItem(STORE))}}catch(e){{}}if(!d)return;
for(const[q,v]of Object.entries(d.answers||{{}})){{const s=document.querySelector(`.case[data-q="${{q}}"]`);if(!s)continue;
for(const n of["settled","verdict"])if(v[n]){{const e=s.querySelector(`input[name="${{q}}-${{n}}"][value="${{v[n]}}"]`);if(e)e.checked=true}}
(v.roots||[]).forEach(r=>{{const e=s.querySelector(`input[name="${{q}}-root"][value="${{r}}"]`);if(e)e.checked=true}});
s.querySelector(`input[name="${{q}}-note"]`).value=v.note||""}}if(d.submitted)reveal()}}
function agree(a,k){{if(a.settled===null)return null;const s=a.settled==="yes";if(s!==k.settled)return false;if(!s)return true;
return a.verdict===k.verdict&&[...a.roots].sort().join()==[...k.root_records].sort().join()}}
function reveal(){{window.SUB=true;const a=collect();let n=0,ok=0;for(const[q,k]of Object.entries(KEY)){{const s=document.querySelector(`.case[data-q="${{q}}"]`);
const r=agree(a[q],k);if(r!==null){{n++;ok+=r?1:0}}s.querySelector(".tag").style.display="inline";
s.querySelector(".result").innerHTML=`<span class="${{r?"ok":"bad"}}">${{r===null?"not answered":r?"agrees with key":"differs from key"}}</span> <span class="mut">key: ${{k.version}} ${{k.gap_type}}, ${{k.settled?k.verdict+" "+k.root_records.join(", "):"undetermined"}}</span>`}}
document.getElementById("summary").textContent=`Agreement: ${{ok}} of ${{n}} answered.`;save()}}
function exportAns(){{const blob=new Blob([JSON.stringify({{sheet:"gap-audit",store:STORE,submitted:window.SUB||false,answers:collect(),key:window.SUB?KEY:null,exported_utc:new Date().toISOString()}},null,1)],{{type:"application/json"}});
const u=URL.createObjectURL(blob),l=document.createElement("a");l.href=u;l.download="gap-audit-answers.json";l.click();URL.revokeObjectURL(u)}}
document.addEventListener("change",save);document.addEventListener("input",save);
document.getElementById("submit").onclick=()=>{{if(confirm("Submit and reveal the key? Answers are locked in your export."))reveal()}};
document.getElementById("export").onclick=exportAns;restore();
</script></body></html>
"""
    open(os.path.join(HERE, "gap-audit.html"), "w", encoding="utf-8", newline="\n").write(page)
    print("wrote gap-audit.html:", chosen)


if __name__ == "__main__":
    main()
