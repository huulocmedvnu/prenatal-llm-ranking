"""Collect every number shown in Figures 2-4 and Tables 1-2 into outputs/fig_data.json."""
import glob, json, os, sys
from statsmodels.stats.proportion import proportion_confint
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = ["x", "/dev/null"]; exec(open(f"{B}/scripts/analyze_primary.py").read().split("res = {")[0])
O = f"{B}/outputs"
PRE = [k for k, c in CASE.items() if c["period"] == "pre"]
for t, lab in [("qwen3_14b", "Qwen3 14B"), ("gpt-oss_20b", "gpt-oss 20B"), ("gemma3_12b", "Gemma 3 12B"), ("llama3_1_8b", "Llama 3.1 8B")]:
    ps = [p for p in [f"{O}/open_{t}.jsonl", f"{O}/open_new_{t}.jsonl"] if os.path.exists(p)]
    r = llm(ps)
    if all(k in r for k in CASE):
        R[lab] = r
LAB = {"resnik": "HPO semantic similarity", "exomiser_hiphive": "Exomiser hiPHIVE", "exomiser_human": "Exomiser human-only",
       "haiku_r1": "Claude Haiku 5.5", "sonnet_r1": "Claude Sonnet 5.5", "opus_r1": "Claude Opus 5.5"}


def prop(r, ks, t):
    x = sum(r[k] <= t for k in ks); lo, hi = proportion_confint(x, len(ks), method="wilson")
    return dict(x=x, n=len(ks), p=100 * x / len(ks), lo=100 * lo, hi=100 * hi)


out = {"methods": {}}
for key, r in R.items():
    if key in ("opus_r2", "opus_r3"):
        continue
    name = LAB.get(key, key)
    out["methods"][name] = {per: {f"top{t}": prop(r, ks, t) for t in (1, 10, 50)} for per, ks in [("pre", PRE), ("post", POST)]}
ref = [R["exomiser_hiphive"][k] <= 10 for k in POST]
out["diff_post"] = {}
for key, r in R.items():
    if key in ("opus_r2", "opus_r3", "exomiser_hiphive"):
        continue
    d, lo, hi, p, b, c = newcombe([r[k] <= 10 for k in POST], ref)
    out["diff_post"][LAB.get(key, key)] = dict(diff=d, lo=lo, hi=hi, p=p)
out["adjusted"] = json.load(open(f"{O}/adjusted.json"))
out["analysis_v2"] = json.load(open(f"{O}/analysis_v2.json"))["topk"]
out["v1p"] = {k: {kk: vv for kk, vv in v.items() if kk != "per_case"} for k, v in json.load(open(f"{O}/v1p_results.json")).items()}
out["v1"] = {k: {kk: vv for kk, vv in v.items() if kk != "per_case"} for k, v in json.load(open(f"{O}/v1_results.json")).items()}
out["rag"] = json.load(open(f"{O}/rag_test.json"))
json.dump(out, open(f"{O}/fig_data.json", "w"), indent=1, default=float)
print("methods:", list(out["methods"]))
