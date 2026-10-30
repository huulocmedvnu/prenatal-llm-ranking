"""Per-fetus difficulty features that do not depend on any LLM output.
  n_terms         number of distinct HPO query terms
  mean_ic, max_ic information content of the query terms (HPO 2026 gene annotations)
  exact_frac      fraction of findings whose text equals an HPO label or synonym
  gene_n_terms    HPO annotation count of the causal gene (how well described it is)
  gene_freq_other number of fetuses with the same gene in other cohorts
Writes outputs/difficulty.json."""
import json, os, re, sys
from collections import Counter
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts")); os.chdir(os.path.join(ROOT, "scripts"))
from rank import KB
k26 = KB("2026", "2026")
cases = json.load(open(f"{ROOT}/work/cases_v2.json"))
terms = json.load(open(f"{ROOT}/work/hpo_terms_v2.json"))
labels = set()
for t, d in k26.terms.items():
    labels.add(d.get("name", "").lower())
    for s in d.get("syn", []):
        labels.add(s.lower())
genecount = Counter(g for c in cases for g in set(c["genes"]))
by_cohort = Counter((c["cohort"], g) for c in cases for g in set(c["genes"]))
out = {}
for c in cases:
    k = f"{c['cohort']}|{c['case']}"
    ics = [k26.ic.get(t, 0.0) for t in terms[k] if t in k26.anc]
    gnt = max([len(k26.gene_terms.get(g, ())) for g in c["genes"]] or [0])
    gfo = max([genecount[g] - by_cohort[(c["cohort"], g)] for g in c["genes"]] or [0])
    exact = np.mean([f.strip().lower() in labels for f in c["findings"]]) if c["findings"] else 0.0
    out[k] = dict(n_terms=len(set(terms[k])), mean_ic=float(np.mean(ics)) if ics else 0.0,
                  max_ic=float(max(ics)) if ics else 0.0, exact_frac=float(exact),
                  gene_n_terms=gnt, gene_freq_other=gfo, period=c["period"], cohort=c["cohort"])
json.dump(out, open(f"{ROOT}/work/difficulty.json", "w"))
D = pd.DataFrame(out).T
for col in ["n_terms", "mean_ic", "max_ic", "exact_frac", "gene_n_terms", "gene_freq_other"]:
    D[col] = D[col].astype(float)
print(D.groupby("period")[["n_terms", "mean_ic", "max_ic", "exact_frac", "gene_n_terms", "gene_freq_other"]].median().round(2).to_string())
