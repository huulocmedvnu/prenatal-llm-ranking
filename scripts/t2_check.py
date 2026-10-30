"""Recall probe by cohort vs popularity priors (leave-cohort-out B1 and leave-one-fetus-out
within the same cohort B1w). If recall ~ B1w, the model knows the cohort's gene spectrum,
not individual cases. Also: case-specific test, recall rank of the true gene vs genes of other
fetuses in the same cohort."""
import os, json, importlib.util
from collections import Counter
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("a", f"{B}/scripts/analyze_v2.py")
import sys; sys.argv = ["x", "/dev/null"]
src = open(f"{B}/scripts/analyze_v2.py").read().split("R = {")[0]
exec(src)


def pop_within(k):
    cnt = Counter(g for k2 in K if k2[0] == k[0] and k2 != k for g in causal[k2])
    ranked = sorted(cnt.items(), key=lambda x: -x[1]); best = 1001.0
    for g, n in ranked:
        if g in causal[k]:
            best = min(best, sum(m > n for _, m in ranked) + (sum(m == n for _, m in ranked) + 1) / 2)
    return best


B1w = {k: pop_within(k) for k in K}
B1 = popularity(False)
runs = {m: llm_ranks(f"{B}/outputs/{m}-5-5_T2.jsonl") for m in ["haiku", "sonnet", "opus"]}
for coh in ["fu2022", "smogavec2022", "graham2026", "aogs2026"]:
    ks = [k for k in K if k[0] == coh]
    line = f"{coh:13s} n={len(ks):3d}  B1(other cohorts) {sum(B1[k]<=10 for k in ks):3d}  B1w(same cohort) {sum(B1w[k]<=10 for k in ks):3d}"
    for m, r in runs.items():
        line += f"  {m} T2 top10 {sum(r[k]<=10 for k in ks):3d} top1 {sum(r[k]<=1 for k in ks)}"
    print(line)
# case-specificity: for Opus T2, is the same gene list returned for every case of a cohort?
for m in ["opus", "sonnet"]:
    lists = {}
    for line in open(f"{B}/outputs/{m}-5-5_T2.jsonl"):
        x = json.loads(line); lists.setdefault(x["cohort"], []).append(tuple((x.get("genes") or [])[:10]))
    for coh, L in lists.items():
        print(m, coh, "distinct top-10 lists:", len(set(L)), "of", len(L))
