"""Combine the pre-cutoff fetuses (335) and the adjudicated post-cutoff extraction (117) into
one case set with Resnik (HPO 2026, same query rules) ranks. Writes outputs/cases_v2.json,
outputs/hpo_terms_v2.json, outputs/resnik_top500_v2.json."""
import json, os, sys
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts")); os.chdir(os.path.join(ROOT, "scripts"))
from rank import KB, nearest_in, rank_of

OLD = pd.read_csv(f"{ROOT}/inputs/pd_hpo/cases.tsv", sep="\t", dtype=str)
NEW = pd.read_csv(f"{ROOT}/inputs_manual/v2_cases.csv", dtype=str).fillna("")
NEW["genes"] = NEW.genes.str.replace(" ", "")
C = pd.concat([OLD[["cohort", "case", "genes", "finding", "hpo_id"]], NEW[["cohort", "case", "genes", "finding", "hpo_id"]]])
FIRST_ONLINE = {"fu2022": "2022-11-03", "smogavec2022": "2022-01-04", "graham2026": "2026-04-20", "aogs2026": "2026-07-02"}
k20, k26 = KB("2020", "2020"), KB("2026", "2026")
common = sorted(set(k20.gene_terms) & set(k26.gene_terms))
cases, terms, top = [], {}, {}
for (coh, case), d in C.groupby(["cohort", "case"], sort=False):
    genes = [g for g in d.genes.iloc[0].split(";") if g]
    q26 = list(dict.fromkeys(d.hpo_id))
    q20 = list(dict.fromkeys(filter(None, (nearest_in(k20.terms, k26.anc, k26.terms, q) for q in q26))))
    sc = k26.scores(q20)
    s = sc.reindex(common).fillna(-1.0).rank(ascending=False, method="average").sort_values()
    key = f"{coh}|{case}"
    top[key] = {g: float(v) for g, v in s.head(500).items()}
    terms[key] = q26
    post = coh not in FIRST_ONLINE or FIRST_ONLINE[coh] >= "2026-07-01"
    cases.append(dict(cohort=coh, case=case, genes=genes, findings=list(dict.fromkeys(d.finding)),
                      resnik_rank=rank_of(sc, genes, set(common)), period="post" if post else "pre",
                      source="v2" if coh not in FIRST_ONLINE else "pd"))
json.dump(cases, open(f"{ROOT}/work/cases_v2.json", "w"), indent=0)
json.dump(terms, open(f"{ROOT}/work/hpo_terms_v2.json", "w"))
json.dump(top, open(f"{ROOT}/work/resnik_top500_v2.json", "w"))
df = pd.DataFrame(cases)
print(df.groupby(["source", "period"]).size().to_string())
print("Resnik top-10 post:", (df[df.period == "post"].resnik_rank <= 10).sum(), "/", (df.period == "post").sum())
