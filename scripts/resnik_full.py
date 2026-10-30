"""Full Resnik (HPO 2026) gene ranking per fetus, same query and gene universe as
rank_2026 of the pre-cutoff extraction. Writes the top 500 genes per fetus for rank fusion."""
import os, sys, json
OUT_PATH = os.path.abspath(sys.argv[1])
import pandas as pd

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, "scripts"))
os.chdir(os.path.join(PROJ, "scripts"))
from rank import KB, nearest_in, rank_of  # noqa: E402

out = OUT_PATH
C = pd.read_csv(os.path.join(PROJ, "inputs", "pd_hpo", "cases.tsv"), sep="\t")
k20, k26 = KB("2020", "2020"), KB("2026", "2026")
common = sorted(set(k20.gene_terms) & set(k26.gene_terms))
res = {}
check = []
for (coh, case), d in C.groupby(["cohort", "case"], sort=False):
    genes = d.genes.iloc[0].split(";")
    q26 = list(dict.fromkeys(d.hpo_id))
    q20 = list(dict.fromkeys(filter(None, (nearest_in(k20.terms, k26.anc, k26.terms, q) for q in q26))))
    sc = k26.scores(q20)
    s = sc.reindex(common).fillna(-1.0)
    r = s.rank(ascending=False, method="average").sort_values()
    res[f"{coh}|{case}"] = {g: float(v) for g, v in r.head(500).items()}
    check.append(rank_of(sc, genes, set(common)))
json.dump(res, open(out, "w"))
R = pd.read_csv(os.path.join(PROJ, "inputs", "pd_hpo", "ranks.tsv"), sep="\t")
print("matches ranks.tsv:", (abs(R.rank_2026.values - pd.Series(check).values) < 1e-9).all())
