"""Small derived inputs used by the scoring scripts:
  work/hpo_terms.json        HPO terms per pre-cutoff fetus (order of first appearance)
  work/cases_meta.tsv        organ-system section per pre-cutoff fetus
  work/cases_v2_new.json     the 117 newly extracted post-cutoff fetuses
  work/hpo_terms_v2_new.json their HPO terms"""
import csv, json, os

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = f"{B}/work"

q, sec = {}, {}
for r in csv.DictReader(open(f"{B}/inputs/pd_hpo/cases.tsv"), delimiter="\t"):
    k = r["cohort"] + "|" + r["case"]
    q.setdefault(k, [])
    if r["hpo_id"] not in q[k]:
        q[k].append(r["hpo_id"])
    sec.setdefault((r["cohort"], r["case"]), r["section"])
json.dump(q, open(f"{W}/hpo_terms.json", "w"))
with open(f"{W}/cases_meta.tsv", "w") as w:
    w.write("cohort\tcase\tsection\n")
    for (a, b), s in sec.items():
        w.write(f"{a}\t{b}\t{s}\n")

cases = json.load(open(f"{W}/cases_v2.json"))
terms = json.load(open(f"{W}/hpo_terms_v2.json"))
new = [c for c in cases if c.get("source") == "v2"]
json.dump(new, open(f"{W}/cases_v2_new.json", "w"), indent=0)
json.dump({f"{c['cohort']}|{c['case']}": terms[f"{c['cohort']}|{c['case']}"] for c in new},
          open(f"{W}/hpo_terms_v2_new.json", "w"))
print(len(q), "pre-cutoff fetuses;", len(new), "new post-cutoff fetuses")
