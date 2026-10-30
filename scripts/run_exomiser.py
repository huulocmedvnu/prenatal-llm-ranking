"""Exomiser 15.1.0 phenotype-only gene ranking (REST prioritiser, data 2512).
Modes: hiPHIVE all species + PPI, and hiPHIVE human only. Saves (symbol, score)
for the top 1000 genes per fetus. usage: run_exomiser.py <hpo_terms.json> <out.json>"""
import json, sys, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
BASE = "http://localhost:8085/exomiser-prioritiser/api/v1/prioritise/gene"
terms, out = sys.argv[1:3]
q = json.load(open(terms))


def one(args):
    k, hp, params = args
    a = [("phenotypes", h) for h in hp] + [("prioritiser", "hiphive"), ("limit", "1000")]
    if params:
        a.append(("prioritiser-params", params))
    with urllib.request.urlopen(BASE + "?" + urllib.parse.urlencode(a), timeout=900) as r:
        d = json.load(r)
    return k, [[x["geneSymbol"], x["score"]] for x in d.get("results", [])]


res = {}
for mode, params in [("hiphive_all", ""), ("hiphive_human", "human")]:
    with ThreadPoolExecutor(4) as ex:
        res[mode] = dict(ex.map(one, [(k, hp, params) for k, hp in q.items()]))
    print(mode, "done", len(res[mode]), flush=True)
json.dump(res, open(out, "w"))
