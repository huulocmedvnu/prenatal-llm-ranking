"""Confirmatory and robustness analyses (PLAN_v2). usage: analyze_v2.py <out.json>"""
import csv, glob, json, math, os, sys
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import binomtest, norm as N
import importlib.util

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("sc", f"{B}/scripts/score_lib.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
norm = sc.norm

cases = json.load(open(f"{B}/work/cases.json"))
K = [(c["cohort"], str(c["case"])) for c in cases]
CASE = {(c["cohort"], str(c["case"])): c for c in cases}
causal = {k: {norm(g)[0] for g in CASE[k]["genes"]} for k in K}
gap = json.load(open(f"{B}/work/annot_gap.json"))
section = {}
with open(f"{B}/work/cases_meta.tsv") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        section[(r["cohort"], r["case"])] = r["section"]
POST = [k for k in K if CASE[k]["period"] == "post"]
res = {}


def llm_ranks(path):
    r = {}
    for line in open(path):
        x = json.loads(line)
        k = (x["cohort"], str(x["case"]))
        seen, lst = set(), []
        for g in (x.get("genes") or []):
            s = norm(g)[0]
            if s not in seen:
                seen.add(s); lst.append(s)
        r[k] = next((i + 1 for i, s in enumerate(lst[:50]) if s in causal[k]), 1001)
    return r


def exo_ranks(mode):
    exo = json.load(open(f"{B}/outputs/exomiser_2512.json"))[mode]
    r = {}
    for k in K:
        lst, best = exo["|".join(k)], 1001.0
        for sym, s in lst:
            if norm(sym)[0] in causal[k]:
                best = min(best, sum(t > s for _, t in lst) + (sum(t == s for _, t in lst) + 1) / 2)
        r[k] = best
    return r


def popularity(by_section):
    """leave-cohort-out gene frequency; optional restriction to the same organ system"""
    r = {}
    for k in K:
        cnt = Counter()
        for k2 in K:
            if k2[0] == k[0]:
                continue
            if by_section and section.get(k2) != section.get(k):
                continue
            for g in causal[k2]:
                cnt[g] += 1
        ranked = sorted(cnt.items(), key=lambda x: -x[1])
        best = 1001.0
        for g, n in ranked:
            if g in causal[k]:
                best = min(best, sum(m > n for _, m in ranked) + (sum(m == n for _, m in ranked) + 1) / 2)
        r[k] = best
    return r


def top(r, ks, t=10):
    return [r[k] <= t for k in ks]


def newcombe_paired(a, b):
    """Newcombe (1998) method 10 CI for difference of paired proportions a - b"""
    n = len(a)
    A = sum(x and y for x, y in zip(a, b)); Bc = sum(x and not y for x, y in zip(a, b))
    C = sum(y and not x for x, y in zip(a, b)); D = n - A - Bc - C
    z = N.ppf(0.975)

    def wilson(x, n):
        p = x / n; d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - h, c + h
    p1, p2 = (A + Bc) / n, (A + C) / n
    l1, u1 = wilson(A + Bc, n); l2, u2 = wilson(A + C, n)
    den = (A + Bc) * (C + D) * (A + C) * (Bc + D)
    phi = 0 if den == 0 else (A * D - Bc * C) / math.sqrt(den)
    dlt = p1 - p2
    lo = dlt - math.sqrt(max((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2, 0))
    hi = dlt + math.sqrt(max((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2, 0))
    pval = binomtest(Bc, Bc + C).pvalue if Bc + C else 1.0
    return round(100 * dlt, 1), round(100 * lo, 1), round(100 * hi, 1), pval


def cluster_boot(a, b, ks, nb=2000, seed=1):
    """bootstrap of the paired difference, resampling causal genes (clusters)"""
    rng = np.random.default_rng(seed)
    gk = defaultdict(list)
    for i, k in enumerate(ks):
        gk[sorted(causal[k])[0]].append(i)
    groups = list(gk.values()); a = np.array(a, float); b = np.array(b, float)
    ds = []
    for _ in range(nb):
        idx = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        ds.append(a[idx].mean() - b[idx].mean())
    return [round(100 * x, 1) for x in np.percentile(ds, [2.5, 97.5])]


R = {"exomiser_all": exo_ranks("hiphive_all"), "exomiser_human": exo_ranks("hiphive_human"),
     "resnik": {k: CASE[k]["resnik_rank"] for k in K},
     "B1_popularity": popularity(False), "B2_popularity_system": popularity(True)}
for p in sorted(glob.glob(f"{B}/outputs/*-5-5_*.jsonl")) + sorted(glob.glob(f"{B}/outputs/open_*.jsonl")):
    n = sum(1 for _ in open(p))
    if n == len(K):
        R[os.path.basename(p)[:-6]] = llm_ranks(p)

# 1. top-k table, all and post-cutoff
tab = {}
for name, r in R.items():
    tab[name] = {sub: {f"top{t}": int(sum(top(r, ks, t))) for t in (1, 5, 10, 50)} | {"n": len(ks)}
                 for sub, ks in [("all", K), ("post", POST)]}
res["topk"] = tab

# 2. primary: LLM r1 vs Exomiser hiPHIVE, post-cutoff; Holm over 3 models
prim = {}
for m in ["haiku-5-5_r1", "sonnet-5-5_r1", "opus-5-5_r1"]:
    if m not in R:
        continue
    for sub, ks in [("post", POST), ("all", K)]:
        d, lo, hi, p = newcombe_paired(top(R[m], ks), top(R["exomiser_all"], ks))
        prim[f"{m}|{sub}"] = dict(diff=d, ci=[lo, hi], p=p,
                                  gene_cluster_boot=cluster_boot(top(R[m], ks), top(R["exomiser_all"], ks), ks))
ps = sorted((v["p"], k) for k, v in prim.items() if k.endswith("|post"))
for i, (p, k) in enumerate(ps):
    prim[k]["p_holm"] = min(1.0, max(p * (len(ps) - j) for j, (pp, kk) in enumerate(ps[: i + 1])))
res["primary"] = prim

# 3. annotation-gap strata (top-10 counts)
strata = {"none": [], "some": [], "all": []}
for k in K:
    a, b = gap["|".join(k)]
    strata["none" if a == 0 else "all" if a == b else "some"].append(k)
res["annotation_gap"] = {s: {m: f"{sum(top(R[m], ks))}/{len(ks)}" for m in R if not m.startswith(("haiku-5-5_N1", "T2"))}
                         for s, ks in strata.items()}

# 4. replicate agreement (top-10) for each Claude model
agree = {}
for m in ["haiku", "sonnet", "opus"]:
    reps = [R.get(f"{m}-5-5_r{i}") for i in (1, 2, 3)]
    if all(reps):
        t = np.array([top(r, K) for r in reps], int)
        agree[m] = {"top10_each": t.sum(1).tolist(), "all3_agree_pct": round(100 * np.mean(t.min(0) == t.max(0)), 1),
                    "any_rep_top10": int(t.max(0).sum()), "all_reps_top10": int(t.min(0).sum())}
res["replicates"] = agree
json.dump(res, open(sys.argv[1], "w"), indent=1)

print("TOP-10 (all / post-cutoff)")
for name in R:
    print(f"  {name:28s} {tab[name]['all']['top10']:4d}/{len(K)}  {tab[name]['post']['top10']:3d}/{len(POST)}  top1 {tab[name]['all']['top1']}")
print("PRIMARY (top-10 difference vs Exomiser hiPHIVE, pct points)")
for k, v in prim.items():
    print(f"  {k:24s} diff {v['diff']} CI {v['ci']} p {v['p']:.2e} holm {v.get('p_holm', '')} geneboot {v['gene_cluster_boot']}")
print("ANNOTATION GAP", json.dumps(res["annotation_gap"], indent=0)[:1500])
print("REPLICATES", agree)
