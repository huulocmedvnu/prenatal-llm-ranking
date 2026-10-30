import os, csv
from collections import defaultdict
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


