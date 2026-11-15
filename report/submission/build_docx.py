import sys, re, copy, subprocess, os
from docx.text.paragraph import Paragraph
import docx
R = r"C:/Users/Liezl/Documents/Obsidian/06 Strategy/competitions/AI x Epistemics Research Sprint"
SRC = R + "/report/draft-report.condensed.md"
TPL = r"C:/Users/Liezl/Downloads/Copy of Apart Research hackathon submission template.docx"
OUT = R + "/report/submission/Phantom-Witnesses-submission.docx"
TMP = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
s = open(SRC, encoding="utf-8").read()
lines = s.split("\n")
title = lines[0].lstrip("# ").strip()
authors = re.sub(r"\*\*", "", lines[2]).strip()
venue = re.sub(r"\^\[.*\]$", "", lines[4]).strip()
a = s.index("## Abstract"); b = s.index("## 1. Introduction")
abstract = s[a:b].split("\n", 1)[1].strip()
body = s[b:]
body = body.replace("(moved from Appendix H.1 to H.3 and 4.6 to 4.8)", "(moved from Sections 3.15 to 3.17 and 4.6 to 4.8)")
# drop duplicate figure inside Appendix K
md = TMP + "/body.md"
open(md, "w", encoding="utf-8").write(body)
pd = TMP + "/body.docx"
subprocess.run([r"C:/Users/Liezl/tools/pandoc/pandoc.exe", md, "-f", "markdown-implicit_figures", "-o", pd,
                "--reference-doc", TPL, "--resource-path", R + "/report"], check=True)
import zipfile, shutil
z = zipfile.ZipFile(pd); items = {n: z.read(n) for n in z.namelist()}; z.close()
ct = items["[Content_Types].xml"].decode()
if 'Extension="ttf"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="ttf" ContentType="application/x-font-ttf"/><Default ', 1)
items["[Content_Types].xml"] = ct.encode()
with zipfile.ZipFile(pd, "w", zipfile.ZIP_DEFLATED) as z:
    for n, v in items.items(): z.writestr(n, v)
d = docx.Document(pd)
t = docx.Document(TPL)
tbl = copy.deepcopy(t.tables[0]._tbl)
# fill title block
from docx.table import Table
T = Table(tbl, d._body)
cells = [r.cells[0] for r in T.rows]
tp = [p for p in cells[0].paragraphs if p.text.strip() == "PROJECT TITLE"][0]
tp.runs[0].text = title
for r in tp.runs[1:]: r.text = ""
for cc in cells:
    for el in list(cc._tc):
        if el.tag.split('}')[1] == 'tbl': cc._tc.remove(el)
for p in [q for cc in cells for q in cc.paragraphs]:
    if p._p is not tp._p and p.text.strip() in ("With", "Apart Research", "With Apart Research"):
        p._p.getparent().remove(p._p)
from docx.enum.text import WD_ALIGN_PARAGRAPH
for txt, it in ((authors, False), (venue, True)):
    q = copy.deepcopy(tp._p); tp._p.getparent().append(q)
    Q = Paragraph(q, cells[0])
    for r in Q.runs[1:]: r._r.getparent().remove(r._r)
    Q.style = d.styles["Normal"] if "Normal" in [x.name for x in d.styles] else Q.style
    Q.runs[0].text = txt; Q.runs[0].italic = it; Q.runs[0].bold = False
    from docx.shared import Pt
    Q.runs[0].font.size = Pt(11 if not it else 10)
    Q.alignment = WD_ALIGN_PARAGRAPH.CENTER
ac = [c for c in cells if "Abstract" in c.text][0]
ap = [p for p in ac.paragraphs if p.text.strip() == "Abstract"][0]
for r in ap.runs: r.bold = True
newp = copy.deepcopy(ap._p); ap._p.addnext(newp)
from docx.text.paragraph import Paragraph
P = Paragraph(newp, ac)
for r in P.runs[1:]: r._r.getparent().remove(r._r)
P.runs[0].text = abstract; P.runs[0].bold = False
body_el = d.element.body
body_el.insert(0, tbl)
# table borders + small font for tables in body
for tb in d.tables[1:]:
    tb.style = d.styles["Table"] if "Table" in [x.name for x in d.styles] else tb.style
d.save(OUT)
print(OUT)
