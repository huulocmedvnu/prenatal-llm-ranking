"""Long-format data for mixed models: one row per fetus x method (top-10 indicator)."""
import os, csv, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = ["x", "/dev/null"]; exec(open(f"{B}/scripts/analyze_primary.py").read().split("res = {")[0])
w = csv.writer(open(f"{B}/outputs/mixed_long.csv", "w"))
w.writerow(["fetus", "gene", "cohort", "period", "method", "top10"])
for k, c in CASE.items():
    g = sorted(causal[k])[0]
    for m in ["exomiser_hiphive", "opus_r1", "sonnet_r1", "haiku_r1"]:
        w.writerow(["|".join(k), g, k[0], c["period"], m, int(R[m][k] <= 10)])
print("rows written", 4 * len(CASE))
