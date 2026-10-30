"""Is the lower LLM accuracy in post-cutoff fetuses explained by case difficulty?
Logistic regression of LLM top-10 on period (post vs pre), unadjusted and adjusted for
difficulty features that do not depend on the LLM; the same model for Exomiser as a check;
and propensity-matched comparison (each post fetus matched to 2 pre fetuses).
usage: adjusted.py <out.json>"""
import os, json, sys
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.neighbors import NearestNeighbors

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(f"{B}/scripts/analyze_primary.py").read().split("res = {")[0]
sys_argv = sys.argv; sys.argv = ["x", "/dev/null"]; exec(src); sys.argv = sys_argv

D = pd.DataFrame(json.load(open(f"{B}/work/difficulty.json"))).T
for c in ["n_terms", "mean_ic", "max_ic", "exact_frac", "gene_n_terms", "gene_freq_other"]:
    D[c] = D[c].astype(float)
keys = {f"{a}|{b}": (a, b) for a, b in CASE}
D["post"] = (D.period == "post").astype(int)
for m in ["opus_r1", "opus_r2", "opus_r3", "sonnet_r1", "haiku_r1", "exomiser_hiphive", "resnik"]:
    D[m] = [int(R[m][keys[k]] <= 10) for k in D.index]
D["opus_mean"] = D[["opus_r1", "opus_r2", "opus_r3"]].mean(axis=1)
D["exo_top50"] = [int(R["exomiser_hiphive"][keys[k]] <= 50) for k in D.index]
D["log_terms"] = np.log(D.n_terms.clip(lower=1))
D["log_gene_terms"] = np.log1p(D.gene_n_terms)
D["log_gene_freq"] = np.log1p(D.gene_freq_other)
COV = "log_terms + mean_ic + exact_frac + log_gene_terms + log_gene_freq + exo_top50"
out = {"n": D.post.value_counts().to_dict(), "models": {}}


def fit(y, cov):
    f = f"{y} ~ post" + (f" + {cov}" if cov else "")
    m = smf.glm(f, D, family=sm.families.Binomial()).fit(cov_type="HC1")
    b, (lo, hi) = m.params["post"], m.conf_int().loc["post"]
    return dict(OR=round(float(np.exp(b)), 2), ci=[round(float(np.exp(lo)), 2), round(float(np.exp(hi)), 2)],
                p=float(m.pvalues["post"]))


for y in ["opus_r1", "sonnet_r1", "haiku_r1", "exomiser_hiphive", "resnik"]:
    out["models"][y] = {"unadjusted": fit(y, ""), "adjusted": fit(y, COV)}
    cov_noexo = COV.replace(" + exo_top50", "")
    out["models"][y]["adjusted_no_exomiser_term"] = fit(y, cov_noexo)

# propensity matching: post fetus -> 2 nearest pre fetuses on the logit of P(post | features)
ps = smf.glm(f"post ~ {COV}", D, family=sm.families.Binomial()).fit()
D["lp"] = np.log(ps.fittedvalues / (1 - ps.fittedvalues))
pre, post = D[D.post == 0], D[D.post == 1]
nn = NearestNeighbors(n_neighbors=2).fit(pre[["lp"]].values)
_, idx = nn.kneighbors(post[["lp"]].values)
matched_pre = pre.iloc[idx.ravel()]
rng = np.random.default_rng(1)
mt = {}
for y in ["opus_r1", "sonnet_r1", "haiku_r1", "exomiser_hiphive", "resnik"]:
    a, b = post[y].values, matched_pre[y].values.reshape(-1, 2).mean(1)
    boots = []
    for _ in range(4000):
        i = rng.integers(0, len(a), len(a)); boots.append(a[i].mean() - b[i].mean())
    mt[y] = dict(post=round(100 * a.mean(), 1), matched_pre=round(100 * b.mean(), 1),
                 diff=round(100 * (a.mean() - b.mean()), 1), ci=[round(100 * x, 1) for x in np.percentile(boots, [2.5, 97.5])])
out["matched"] = mt
out["balance"] = {c: [round(float(post[c].mean()), 2), round(float(matched_pre[c].mean()), 2), round(float(pre[c].mean()), 2)]
                  for c in ["log_terms", "mean_ic", "exact_frac", "log_gene_terms", "log_gene_freq", "exo_top50"]}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print("n", out["n"])
for y, v in out["models"].items():
    print(f"{y:17s} OR(post) unadj {v['unadjusted']['OR']} {v['unadjusted']['ci']}  adj {v['adjusted']['OR']} {v['adjusted']['ci']} p {v['adjusted']['p']:.3g}")
print("MATCHED (post vs difficulty-matched pre, % top-10)")
for y, v in mt.items():
    print(f"  {y:17s} post {v['post']}  matched pre {v['matched_pre']}  diff {v['diff']} CI {v['ci']}")
print("BALANCE post / matched pre / all pre:", out["balance"])
