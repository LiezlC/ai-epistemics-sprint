"""Over-commitment chart: share of the 40 gap bundles answered "undetermined" with no handoff note, per arm.
Reads the gap-set score files in the team repo layout (sprint-code/scored-run/gap-set/). Writes PNG and SVG.
Usage: python -I make_fig.py <gap-set folder> <out folder>
"""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

gap, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
d = json.load(open(os.path.join(gap, "scores.json"), encoding="utf-8"))["arms"]
v2 = json.load(open(os.path.join(gap, "scores_v2.json"), encoding="utf-8"))["arms"]
l3 = json.load(open(os.path.join(gap, "scores_loop_r3.json"), encoding="utf-8"))["arms"]


def share(arms, key):
    x = arms[key]["gap"]["by_label"]["none"]
    n = x["n"]
    return round(x["undetermined_rate"] * n), n


rows = [  # (label, k, n, group)
    ("27b", *share(d, "27b"), "untuned"),
    ("DeepSeek V4 Pro", *share(d, "deepseek"), "untuned"),
    ("4B zero-shot", *share(d, "4b_base"), "untuned"),
    ("GLM 5.2", *share(d, "glm"), "untuned"),
    ("Kimi K3.1 Pro", *share(d, "kimi"), "untuned"),
    ("4B tuned, DPO v1", *share(v2, "4b_tuned_v1"), "tuned"),
    ("4B tuned, DPO v2", *share(v2, "4b_tuned_v2"), "tuned"),
    ("4B tuned, loop round 3", *share(l3, "loop_r3_zero"), "tuned"),
]
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dcdad4"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=300)
fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
ys = []
y = 0
for i, (lab, k, n, g) in enumerate(rows):
    if i == 5:
        y += 0.6  # gap between the two groups
    ys.append(y); y += 1
for (lab, k, n, g), yy in zip(rows, ys):
    ax.barh(yy, k / n, height=0.52, color=BLUE if g == "untuned" else ORANGE, zorder=3)
    ax.text(k / n + 0.015, yy, f"{k}/{n}  ({int(100 * k / n + 0.5)}%)", va="center", ha="left", color=INK, fontsize=8)
v1y = ys[5]
ax.text(0.02, v1y, "collapsed: also “undetermined” on every control", va="center", ha="left", color="white", fontsize=7.5, fontweight="bold", zorder=4)
ax.axvline(1.0, color=MUTED, linestyle=(0, (4, 3)), linewidth=1.0, zorder=2)
ax.text(0.995, -0.95, "keyed answer: undetermined on all 40", ha="right", va="bottom", color=MUTED, fontsize=7.5)
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], color=INK)
ax.invert_yaxis()
ax.set_xlim(0, 1.18); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], color=MUTED)
ax.set_xlabel("Gap bundles answered “undetermined”, no handoff note (n = 40)", color=MUTED, fontsize=8.5)
ax.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID); ax.tick_params(length=0)
ax.legend(handles=[Patch(color=BLUE, label="untuned"), Patch(color=ORANGE, label="preference-tuned 4B")],
          loc="upper right", frameon=True, facecolor="#fcfcfb", edgecolor="#fcfcfb", framealpha=1.0, fontsize=8, bbox_to_anchor=(0.93, 0.93))
fig.tight_layout()
for ext in ("png", "svg"):
    fig.savefig(os.path.join(out, "fig-overcommitment-draft." + ext), facecolor=fig.get_facecolor())
print("wrote", out, [(r[0], r[1], r[2]) for r in rows])
