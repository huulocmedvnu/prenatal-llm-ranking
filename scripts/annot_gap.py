"""Per fetus: how many query findings (or their descendants) are annotated to the causal
gene in HPO 2026. Output: {cohort|case: [n_annotated, n_terms]}"""
import os, sys, json
OUT_PATH = os.path.abspath(sys.argv[1])
import pandas as pd
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, "scripts")); os.chdir(os.path.join(PROJ, "scripts"))
from rank import KB
k26 = KB("2026", "2026")
C = pd.read_csv(os.path.join(PROJ, "inputs", "pd_hpo", "cases.tsv"), sep="\t")
out = {}
for (coh, case), d in C.groupby(["cohort", "case"], sort=False):
    genes = d.genes.iloc[0].split(";")
    terms = list(dict.fromkeys(d.hpo_id))
    ann = set().union(*[k26.gene_terms.get(g, set()) for g in genes]) if genes else set()
    # a finding counts as annotated when the gene set contains the term itself or a descendant
    n = 0
    for t in terms:
        if t in ann or any(t in k26.anc.get(a, set()) for a in ann):
            n += 1
    out[f"{coh}|{case}"] = [n, len(terms)]
json.dump(out, open(OUT_PATH, "w"))
v = list(out.values())
print("none", sum(a == 0 for a, b in v), "some", sum(0 < a < b for a, b in v), "all", sum(a == b for a, b in v))
