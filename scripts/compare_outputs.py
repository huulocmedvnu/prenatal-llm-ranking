"""Compare regenerated files with the committed reference copies.
JSON: same keys, numbers equal within 1e-9 (relative). Text and TSV: identical, except outputs/mixed.txt, whose
numbers may differ by up to 5% between lme4 versions (reported values: R 4.3.3, lme4 2.1.0; with lme4 2.0.6 the
reported interaction odds ratios, P values and variance components differ by less than 1%, and the unreported
conditional main-effect odds ratios, which exceed 300, by up to 2.3%).
usage: compare_outputs.py <reference_dir> <regenerated_dir> [file ...]   (prints REPRODUCED when all agree)"""
import json, os, re, sys

ref_dir, new_dir, files = sys.argv[1], sys.argv[2], sys.argv[3:]
bad = []


def walk(a, b, p):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            bad.append(f"{p}: keys differ {sorted(set(a) ^ set(b))[:5]}")
        for k in set(a) & set(b):
            walk(a[k], b[k], f"{p}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            bad.append(f"{p}: length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{p}[{i}]")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if abs(a - b) > 1e-9 * max(1.0, abs(b)):
            bad.append(f"{p}: {a} vs {b}")
    elif a != b:
        bad.append(f"{p}: {str(a)[:60]} vs {str(b)[:60]}")


NUM = re.compile(r"-?\d+\.\d+|-?\d+")
for f in files:
    r, n = os.path.join(ref_dir, f), os.path.join(new_dir, f)
    if not os.path.exists(n):
        bad.append(f"{f}: not regenerated"); continue
    if f.endswith(".json"):
        walk(json.load(open(n)), json.load(open(r)), f)
    elif f.endswith("mixed.txt"):
        clean = lambda s: [l for l in open(s).read().splitlines() if l.strip() and not re.search(r"LC_|setlocale|During startup|^\d: Setting|Loading required package", l)]
        a, b = clean(n), clean(r)
        if len(a) != len(b):
            bad.append(f"{f}: line count {len(a)} vs {len(b)}")
        for la, lb in zip(a, b):
            xa, xb = NUM.findall(la), NUM.findall(lb)
            if NUM.sub("#", la).split() != NUM.sub("#", lb).split() or len(xa) != len(xb) or any(
                    abs(float(x) - float(y)) > 0.05 * max(1.0, abs(float(y))) for x, y in zip(xa, xb)):
                bad.append(f"{f}: {la.strip()[:70]} | {lb.strip()[:70]}")
    elif open(n, "rb").read() != open(r, "rb").read():
        bad.append(f"{f}: content differs")

print(f"{len(files)} files compared")
for b in bad[:40]:
    print("  DIFF", b)
print("REPRODUCED" if not bad else f"NOT REPRODUCED ({len(bad)} differences)")
sys.exit(1 if bad else 0)
