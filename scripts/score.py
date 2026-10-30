"""Score LLM gene lists against causal genes; compare with Resnik (HPO 2026).
usage: score.py <out.tsv> <run1.jsonl> [run2.jsonl ...]"""
import os, csv, json, sys, math
from collections import defaultdict
from scipy.stats import binomtest
from statsmodels.stats.proportion import proportion_confint

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cases = json.load(open(f"{B}/work/cases.json"))
resnik = json.load(open(f"{B}/work/resnik_top500.json"))
key = lambda c: (c["cohort"], str(c["case"]))
CASE = {key(c): c for c in cases}

# HGNC: approved, previous and alias symbols -> approved
approved, prev, alias = set(), {}, defaultdict(set)
with open(f"{B}/data/hgnc_complete_set.txt") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["status"] != "Approved":
            continue
        s = r["symbol"].upper(); approved.add(s)
        for p in filter(None, r["prev_symbol"].strip('"').split("|")):
            prev.setdefault(p.upper(), s)
        for a in filter(None, r["alias_symbol"].strip('"').split("|")):
            alias[a.upper()].add(s)


def norm(g):
    g = g.strip().upper()
    if g in approved: return g, True
    if g in prev: return prev[g], True
    if len(alias.get(g, ())) == 1: return next(iter(alias[g])), True
    return g, False


def mcnemar(a, b):
    """exact McNemar on paired booleans"""
    n10 = sum(x and not y for x, y in zip(a, b)); n01 = sum(y and not x for x, y in zip(a, b))
    return binomtest(n10, n10 + n01).pvalue if n10 + n01 else 1.0, n10, n01


rows = []
for path in sys.argv[2:]:
    recs = [json.loads(l) for l in open(path)]
    model = recs[0]["model"]
    by = {}
    nsym = nbad = nfail = 0
    for r in recs:
        k = (r["cohort"], str(r["case"]))
        c = CASE[k]
        causal = {norm(g)[0] for g in c["genes"]}
        g = r.get("genes")
        if not g:
            nfail += 1; by[k] = 51; continue
        seen, lst = set(), []
        for x in g:
            s, ok = norm(x)
            nsym += 1; nbad += (not ok)
            if s not in seen:
                seen.add(s); lst.append(s)
        rank = next((i + 1 for i, s in enumerate(lst[:50]) if s in causal), 51)
        by[k] = rank
        # reciprocal rank fusion with Resnik
        rr = resnik["|".join(k)]
        score = defaultdict(float)
        for i, s in enumerate(lst[:50]): score[s] += 1 / (60 + i + 1)
        for s, rk in rr.items(): score[s.upper()] += 1 / (60 + rk)
        fused = sorted(score, key=lambda s: -score[s])
        r["fused"] = next((i + 1 for i, s in enumerate(fused) if s in causal), 501)
        r["rank"] = rank
    fus = {(r["cohort"], str(r["case"])): r.get("fused", 501) for r in recs}
    for sub, sel in [("all", lambda c: True), ("pre", lambda c: c["period"] == "pre"),
                     ("post", lambda c: c["period"] == "post"),
                     ("aogs2026", lambda c: c["cohort"] == "aogs2026")]:
        ks = [key(c) for c in cases if sel(c) and key(c) in by]
        n = len(ks)
        llm10 = [by[k] <= 10 for k in ks]
        res10 = [CASE[k]["resnik_rank"] <= 10 for k in ks]
        fus10 = [fus[k] <= 10 for k in ks]
        p, a, b = mcnemar(llm10, res10)
        pf, _, _ = mcnemar(fus10, res10)
        lo, hi = proportion_confint(sum(llm10), n, method="wilson")
        rows.append(dict(model=model, run=path.split("/")[-1], subset=sub, n=n,
                         top1=sum(by[k] <= 1 for k in ks), top5=sum(by[k] <= 5 for k in ks),
                         top10=sum(llm10), top10_pct=round(100 * sum(llm10) / n, 1),
                         ci=f"{100*lo:.1f}-{100*hi:.1f}", top50=sum(by[k] <= 50 for k in ks),
                         resnik_top10=sum(res10), mcnemar_p=round(p, 4), llm_only=a, resnik_only=b,
                         fused_top10=sum(fus10), fused_p=round(pf, 4),
                         parse_fail=nfail, invalid_sym_pct=round(100 * nbad / max(nsym, 1), 1)))
w = csv.DictWriter(open(sys.argv[1], "w"), fieldnames=list(rows[0]), delimiter="\t")
w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["model"][:18].ljust(18), r["subset"].ljust(8), "n", r["n"], "| top10", r["top10"],
          f"({r['top10_pct']}%)", "vs Resnik", r["resnik_top10"], "p", r["mcnemar_p"],
          "| fused", r["fused_top10"], "| top50", r["top50"], "| fail", r["parse_fail"],
          "| bad sym%", r["invalid_sym_pct"])
