"""Summary table: top-k of every method on the same fetuses, McNemar vs Exomiser
(hiPHIVE all) and vs Resnik. usage: compare_all.py <out.tsv>"""
import os, csv, glob, json, sys
import numpy as np
from scipy.stats import binomtest
from statsmodels.stats.proportion import proportion_confint
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import importlib.util
spec = importlib.util.spec_from_file_location("sc", f"{B}/scripts/score_lib.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
norm = sc.norm

cases = json.load(open(f"{B}/work/cases.json"))
K = [(c["cohort"], str(c["case"])) for c in cases]
CASE = {(c["cohort"], str(c["case"])): c for c in cases}
causal = {k: {norm(g)[0] for g in CASE[k]["genes"]} for k in K}
ranks = {"Resnik (HPO 2026)": {k: CASE[k]["resnik_rank"] for k in K}}

# Exomiser: tie-aware (mean) rank; not returned -> 1001
exo = json.load(open(f"{B}/outputs/exomiser_2512.json"))
for mode, lab in [("hiphive_all", "Exomiser hiPHIVE"), ("hiphive_human", "Exomiser human only")]:
    r = {}
    for k in K:
        lst = exo[mode]["|".join(k)]
        best = 1001.0
        for sym, s in lst:
            if norm(sym)[0] in causal[k]:
                higher = sum(1 for _, t in lst if t > s)
                ties = sum(1 for _, t in lst if t == s)
                best = min(best, higher + (ties + 1) / 2)
        r[k] = best
    ranks[lab] = r

# LLM runs (replicate 1 for Claude; open models)
for path in sorted(glob.glob(f"{B}/outputs/*_r1.jsonl")) + sorted(glob.glob(f"{B}/outputs/open_*.jsonl")):
    recs = [json.loads(l) for l in open(path)]
    if len(recs) < len(K):
        continue
    lab = recs[0]["model"]
    r = {}
    for x in recs:
        k = (x["cohort"], str(x["case"]))
        seen, lst = set(), []
        for g in (x.get("genes") or []):
            s = norm(g)[0]
            if s not in seen:
                seen.add(s); lst.append(s)
        r[k] = next((i + 1 for i, s in enumerate(lst[:50]) if s in causal[k]), 1001)
    ranks[lab] = r


def mc(a, b):
    n10 = sum(x and not y for x, y in zip(a, b)); n01 = sum(y and not x for x, y in zip(a, b))
    return binomtest(n10, n10 + n01).pvalue if n10 + n01 else 1.0


rows = []
ref = "Exomiser hiPHIVE"
for sub, sel in [("all", lambda k: True), ("post", lambda k: CASE[k]["period"] == "post"),
                 ("aogs2026", lambda k: k[0] == "aogs2026")]:
    ks = [k for k in K if sel(k)]
    for lab, r in ranks.items():
        t10 = [r[k] <= 10 for k in ks]
        lo, hi = proportion_confint(sum(t10), len(ks), method="wilson")
        rows.append(dict(subset=sub, method=lab, n=len(ks),
                         top1=sum(r[k] <= 1 for k in ks), top10=sum(t10),
                         top10_pct=round(100 * np.mean(t10), 1), ci95=f"{100*lo:.1f}-{100*hi:.1f}",
                         top50=sum(r[k] <= 50 for k in ks),
                         p_vs_exomiser=round(mc(t10, [ranks[ref][k] <= 10 for k in ks]), 5),
                         p_vs_resnik=round(mc(t10, [ranks["Resnik (HPO 2026)"][k] <= 10 for k in ks]), 5)))
w = csv.DictWriter(open(sys.argv[1], "w"), fieldnames=list(rows[0]), delimiter="\t")
w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["subset"].ljust(8), r["method"][:22].ljust(22), "top1", str(r["top1"]).rjust(3),
          "top10", str(r["top10"]).rjust(3), f"({r['top10_pct']}%)".ljust(8), "top50", str(r["top50"]).rjust(3),
          "p_exo", r["p_vs_exomiser"])
