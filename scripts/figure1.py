"""Figure 1: study design schematic (hand-written SVG, Plotly colours, Arial, black text)."""
import os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "docs", "figures")
BLUE, RED, GREEN, PURPLE, K = "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#111111"
W, H = 960, 420


def t(x, y, s, size=13, weight="normal", color=K, anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{s}</text>'


def box(x, y, w, h, color):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-width="1.5"/>'


def arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="1.4" marker-end="url(#a)"/>')


def fetus(x, y, c):
    return (f'<circle cx="{x}" cy="{y}" r="7" fill="{c}"/><ellipse cx="{x+9}" cy="{y+11}" rx="11" ry="8" fill="{c}"/>')


el = ['<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#555"/></marker></defs>',
      f'<rect width="{W}" height="{H}" fill="white"/>']
cols = [(20, "Fetuses with a monogenic diagnosis"), (345, "Gene ranking from the same findings"), (660, "Analyses")]
for x, title in cols:
    el.append(t(x, 30, title, 14, "bold"))
for x in (325, 640):
    el.append(f'<line x1="{x}" y1="15" x2="{x}" y2="{H-15}" stroke="#bbb" stroke-width="1"/>')
# column 1
el += [box(20, 50, 290, 150, BLUE), fetus(45, 78, BLUE), t(75, 85, "Reported before 1 July 2026", 13, "bold", BLUE),
       t(35, 112, "3 cohorts (China, Austria, United Kingdom)"), t(35, 134, "299 fetuses, 735 findings"),
       t(35, 156, "Largest cohort with variants: 185 fetuses"), t(35, 185, "Used for period comparison", 12)]
el += [box(20, 220, 290, 170, RED), fetus(45, 248, RED), t(75, 255, "Reported from 1 July 2026", 13, "bold", RED),
       t(35, 282, "9 publications, 153 fetuses, 367 findings"), t(35, 304, "Two independent extractions"),
       t(35, 326, "With reported variants: 66 fetuses"), t(35, 355, "After model training cutoffs", 12),
       t(35, 375, "Primary analysis", 12)]
# column 2
el += [box(345, 50, 280, 150, PURPLE), t(360, 78, "Findings as text", 13, "bold", PURPLE),
       t(360, 104, "Large language models"), t(360, 126, "Claude Haiku, Sonnet and Opus 5.5"),
       t(360, 148, "Four open-weight models, 8 to 20B"), t(360, 178, "Top 50 genes as HGNC symbols", 12)]
el += [box(345, 220, 280, 170, GREEN), t(360, 248, "Findings as HPO terms", 13, "bold", "#00936b"),
       t(360, 274, "Exomiser 15.1.0, phenotype only"), t(360, 296, "hiPHIVE and human-only"),
       t(360, 318, "HPO semantic similarity"), t(360, 340, "(Resnik, 4,354 genes)"), t(360, 370, "Ranked gene lists", 12)]
el += [arrow(312, 125, 342, 125), arrow(312, 305, 342, 305)]
# column 3
items = [("Primary", "Top 10 in fetuses from 1 July 2026"), ("Period comparison", "Adjusted and propensity-matched"),
         ("Robustness", "Recall probe, shuffled findings, rewording"), ("Retrieval", "Similar cases or Exomiser candidates"),
         ("Clinical simulation", "Variants in benchmark exomes, Exomiser")]
for i, (a, b) in enumerate(items):
    y = 50 + i * 70
    el += [box(660, y, 280, 58, "#555555"), t(675, y + 24, a, 13, "bold"), t(675, y + 45, b, 12)]
el += [arrow(627, 200, 657, 200)]
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(el) + "</svg>"
p = os.path.join(FIG, "figure1.svg"); open(p, "w").write(svg)
subprocess.run(["rsvg-convert", "-z", "4", "-o", os.path.join(FIG, "figure1.png"), p], check=True)
subprocess.run(["rsvg-convert", "-f", "pdf", "-o", os.path.join(FIG, "figure1.pdf"), p], check=True)
print("figure1 written")
