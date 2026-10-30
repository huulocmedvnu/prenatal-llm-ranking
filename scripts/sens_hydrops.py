"""Sensitivity of the primary comparison: exclude the 23 hydrops fetuses (single finding),
and exclude all fetuses with a single finding."""
import os, json, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = ["x", "/dev/null"]; exec(open(f"{B}/scripts/analyze_primary.py").read().split("res = {")[0])
subsets = {"all post": POST,
           "post without hydrops cohort": [k for k in POST if k[0] != "hydrops"],
           "post with >=2 findings": [k for k in POST if len(CASE[k]["findings"]) >= 2]}
for name, ks in subsets.items():
    ref = [R["exomiser_hiphive"][k] <= 10 for k in ks]
    line = f"{name} (n={len(ks)}): exomiser {sum(ref)}"
    for m in ["opus_r1", "sonnet_r1", "haiku_r1"]:
        a = [R[m][k] <= 10 for k in ks]; d, lo, hi, p, b, c = newcombe(a, ref)
        line += f" | {m} {sum(a)} ({100*sum(a)/len(ks):.1f}%) diff {d:.1f} [{lo:.1f}, {hi:.1f}] p {p:.1e}"
    print(line)
