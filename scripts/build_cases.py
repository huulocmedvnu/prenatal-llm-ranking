"""Build one record per fetus: findings as written, causal genes, Resnik rank."""
import csv, json, sys

cases_tsv, ranks_tsv, out = sys.argv[1:4]
POST = {"graham2026", "aogs2026"}

fetus = {}
with open(cases_tsv) as f:
    for r in csv.DictReader(f, delimiter="\t"):
        k = (r["cohort"], r["case"])
        d = fetus.setdefault(k, {"cohort": r["cohort"], "case": r["case"],
                                 "genes": r["genes"], "findings": []})
        if r["finding"] not in d["findings"]:
            d["findings"].append(r["finding"])

with open(ranks_tsv) as f:
    for r in csv.DictReader(f, delimiter="\t"):
        k = (r["cohort"], r["case"])
        fetus[k]["resnik_rank"] = float(r["rank_2026"])

recs = []
for d in fetus.values():
    d["genes"] = [g.strip() for g in d["genes"].replace(";", ",").split(",") if g.strip()]
    d["period"] = "post" if d["cohort"] in POST else "pre"
    recs.append(d)
json.dump(recs, open(out, "w"), indent=1)
print(len(recs), "fetuses;", sum(d["period"] == "post" for d in recs), "post-cutoff")
