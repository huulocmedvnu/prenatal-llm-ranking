"""Primary confirmatory analysis (PLAN_v2): post-cutoff fetuses (first online >= 2026-07-01:
Yao 2026 AOGS + 117 newly extracted), LLM vs Exomiser hiPHIVE, top-10.
usage: analyze_primary.py <out.json>"""
import os, json, math, sys
from collections import defaultdict
import numpy as np
from scipy.stats import binomtest, norm as N
import importlib.util

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("sc", f"{B}/scripts/score_lib.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
norm = sc.norm
cases = json.load(open(f"{B}/work/cases_v2.json"))
CASE = {(c["cohort"], str(c["case"])): c for c in cases}
POST = [k for k, c in CASE.items() if c["period"] == "post"]
causal = {k: {norm(g)[0] for g in CASE[k]["genes"]} for k in CASE}


def llm(paths):
    r = {}
    for p in paths:
        for line in open(p):
            x = json.loads(line); k = (x["cohort"], str(x["case"]))
            seen, lst = set(), []
            for g in (x.get("genes") or []):
                s = norm(g)[0]
                if s not in seen:
                    seen.add(s); lst.append(s)
            r[k] = next((i + 1 for i, s in enumerate(lst[:50]) if s in causal[k]), 1001)
    return r


def exo(mode):
    d = json.load(open(f"{B}/outputs/exomiser_2512.json"))[mode]
    d.update(json.load(open(f"{B}/outputs/exomiser_2512_new.json"))[mode])
    r = {}
    for k in CASE:
        lst, best = d.get("|".join(k), []), 1001.0
        for sym, s in lst:
            if norm(sym)[0] in causal[k]:
                best = min(best, sum(t > s for _, t in lst) + (sum(t == s for _, t in lst) + 1) / 2)
        r[k] = best
    return r


def newcombe(a, b):
    n = len(a); A = sum(x and y for x, y in zip(a, b)); Bc = sum(x and not y for x, y in zip(a, b))
    C = sum(y and not x for x, y in zip(a, b)); D = n - A - Bc - C; z = N.ppf(0.975)

    def w(x):
        p = x / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - h, c + h
    p1, p2 = (A + Bc) / n, (A + C) / n; l1, u1 = w(A + Bc); l2, u2 = w(A + C)
    den = (A + Bc) * (C + D) * (A + C) * (Bc + D); phi = 0 if den == 0 else (A * D - Bc * C) / math.sqrt(den)
    lo = p1 - p2 - math.sqrt(max((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2, 0))
    hi = p1 - p2 + math.sqrt(max((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2, 0))
    return 100 * (p1 - p2), 100 * lo, 100 * hi, (binomtest(Bc, Bc + C).pvalue if Bc + C else 1.0), Bc, C


def boot(a, b, ks, nb=4000):
    rng = np.random.default_rng(1); gk = defaultdict(list)
    for i, k in enumerate(ks):
        gk[sorted(causal[k])[0]].append(i)
    G = list(gk.values()); a = np.array(a, float); b = np.array(b, float); ds = []
    for _ in range(nb):
        idx = np.concatenate([G[j] for j in rng.integers(0, len(G), len(G))]); ds.append(a[idx].mean() - b[idx].mean())
    return np.percentile(ds, [2.5, 97.5]).round(3) * 100


O = f"{B}/outputs"
R = {"exomiser_hiphive": exo("hiphive_all"), "exomiser_human": exo("hiphive_human"),
     "resnik": {k: c["resnik_rank"] for k, c in CASE.items()}}
for m in ["opus", "sonnet", "haiku"]:
    R[f"{m}_r1"] = llm([f"{O}/{m}-5-5_r1.jsonl", f"{O}/{m}-5-5_new_r1.jsonl"])
for r in (2, 3):
    R[f"opus_r{r}"] = llm([f"{O}/opus-5-5_r{r}.jsonl", f"{O}/opus-5-5_new_r{r}.jsonl"])

res = {"n_post": len(POST), "by_source": {}, "topk": {}, "primary": {}}
for name, r in R.items():
    res["topk"][name] = {f"top{t}": int(sum(r[k] <= t for k in POST)) for t in (1, 5, 10, 50)}
ref = [R["exomiser_hiphive"][k] <= 10 for k in POST]
rows = []
for m in ["opus_r1", "sonnet_r1", "haiku_r1"]:
    a = [R[m][k] <= 10 for k in POST]
    d, lo, hi, p, b, c = newcombe(a, ref)
    rows.append((p, m, d, lo, hi, b, c, boot(a, ref, POST).tolist()))
rows.sort()
for i, (p, m, d, lo, hi, b, c, bt) in enumerate(rows):
    holm = min(1.0, max(pp * (len(rows) - j) for j, (pp, *_) in enumerate(rows[: i + 1])))
    res["primary"][m] = dict(diff=round(d, 1), ci=[round(lo, 1), round(hi, 1)], p=p, p_holm=holm,
                             llm_only=b, exomiser_only=c, gene_cluster_boot=bt)
# per source cohort (top-10 counts)
for coh in sorted({k[0] for k in POST}):
    ks = [k for k in POST if k[0] == coh]
    res["by_source"][coh] = {n: f"{sum(r[k] <= 10 for k in ks)}/{len(ks)}" for n, r in R.items()}
json.dump(res, open(sys.argv[1], "w"), indent=1, default=float)
print("post-cutoff fetuses:", len(POST))
for n, v in res["topk"].items():
    print(f"  {n:18s} top1 {v['top1']:3d} top10 {v['top10']:3d} ({100*v['top10']/len(POST):.1f}%) top50 {v['top50']}")
for m, v in res["primary"].items():
    print(f"  PRIMARY {m}: diff {v['diff']} CI {v['ci']} p {v['p']:.2e} holm {v['p_holm']:.2e} boot {v['gene_cluster_boot']}")
for coh, v in res["by_source"].items():
    print(f"  {coh:16s} opus {v['opus_r1']:>6s} exo {v['exomiser_hiphive']:>6s} resnik {v['resnik']:>6s}")
