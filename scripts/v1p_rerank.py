"""V1 (post-cutoff): LLM re-ranks Exomiser's top-50 genes (alphabetical); score Exomiser alone,
LLM re-rank and RRF fusion, with paired tests. usage: v1p_rerank.py submit <model> | score"""
import glob, json, os, sys
from scipy.stats import binomtest
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = f"{B}/v1p"
man = json.load(open(f"{V}/manifest.json"))
cases = {f"{c['cohort']}|{c['case']}": c for c in json.load(open(f"{B}/work/cases_v2.json"))}


def exomiser_genes(fid):
    p = f"{V}/results/{fid}.genes.tsv"
    if not os.path.exists(p):
        return []
    rows = [l.rstrip("\n").split("\t") for l in open(p) if l.strip()]
    gi = [h.lstrip("#") for h in rows[0]].index("GENE_SYMBOL")
    return list(dict.fromkeys(r[gi] for r in rows[1:]))


if sys.argv[1] == "submit":
    model = sys.argv[2]; sub = []
    for fid, m in man.items():
        g = exomiser_genes(fid)[:50]
        if not g:
            continue
        c = cases[m["key"]]
        sub.append(dict(cohort=c["cohort"], case=c["case"], genes=m["genes"], findings=c["findings"],
                        prompt=("A fetus has the following findings on prenatal ultrasound:\n"
                                + "\n".join("- " + f for f in c["findings"])
                                + "\n\nChromosomal microarray was normal. Exome sequencing found rare candidate variants "
                                  "in the following genes (alphabetical order):\n" + ", ".join(sorted(g))
                                + "\n\nRank these candidate genes from most to least likely to be the causal gene for "
                                  "this fetus. Use only genes from the list, as HGNC symbols.")))
    json.dump(sub, open(f"{V}/rerank_cases.json", "w"))
    os.system(f"cd {B} && venv/bin/python scripts/claude_batch.py submit {V}/rerank_cases.json "
              f"v1p_rerank_{model.replace('claude-', '')} {model} 1")
else:
    import importlib.util
    spec = importlib.util.spec_from_file_location("sc", f"{B}/scripts/score_lib.py")
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    key2fid = {m["key"]: f for f, m in man.items()}
    out = {}
    for path in sorted(glob.glob(f"{B}/outputs/v1p_rerank_*.jsonl")):
        tag = os.path.basename(path)[:-6]
        llm = {}
        for l in open(path):
            x = json.loads(l); llm[key2fid[f"{x['cohort']}|{x['case']}"]] = x.get("genes") or []
        res = []
        for fid, m in man.items():
            ex = exomiser_genes(fid)
            if not ex:
                continue
            causal = {sc.norm(g)[0] for g in m["genes"]}
            exr = next((i + 1 for i, g in enumerate(ex) if sc.norm(g)[0] in causal), 9999)
            top50 = [sc.norm(g)[0] for g in ex[:50]]
            lst = [x for x in dict.fromkeys(sc.norm(g)[0] for g in llm.get(fid, [])) if x in top50]
            lst += [g for g in top50 if g not in lst]
            llr = next((i + 1 for i, g in enumerate(lst) if g in causal), exr) if exr <= 50 else exr
            fused = sorted(top50, key=lambda g: -(1 / (61 + top50.index(g)) + 1 / (61 + lst.index(g))))
            fur = next((i + 1 for i, g in enumerate(fused) if g in causal), exr) if exr <= 50 else exr
            res.append((m["key"], exr, llr, fur))
        o = {"n": len(res), "exomiser_top50": sum(r[1] <= 50 for r in res)}
        for i, lab in [(1, "exomiser"), (2, "llm_rerank"), (3, "fusion")]:
            o[lab] = {f"top{t}": sum(r[i] <= t for r in res) for t in (1, 5, 10)}
        for i, lab in [(2, "llm_rerank"), (3, "fusion")]:
            for t in (1, 5):
                g = sum(r[i] <= t and not r[1] <= t for r in res); l = sum(r[1] <= t and not r[i] <= t for r in res)
                o[f"{lab}_vs_exomiser_top{t}"] = dict(gain=g, loss=l, p=binomtest(g, g + l).pvalue if g + l else 1.0)
        o["per_case"] = res
        out[tag] = o
        print(tag, json.dumps({k: v for k, v in o.items() if k != "per_case"}))
    json.dump(out, open(f"{B}/outputs/v1p_results.json", "w"), indent=1)
