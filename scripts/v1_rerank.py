"""V1 step 2: LLM re-ranks Exomiser's top-50 candidate genes (given alphabetically, so the
Exomiser order is not revealed). Then scores Exomiser alone, LLM re-rank, and their rank
fusion. usage: v1_rerank.py submit <model> | v1_rerank.py score"""
import csv, glob, json, os, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = f"{B}/v1"
man = json.load(open(f"{V}/manifest.json"))
cases = {c["case"]: c for c in json.load(open(f"{B}/work/cases_v2.json")) if c["cohort"] == "fu2022"}


def exomiser_genes(case):
    fs = glob.glob(f"{V}/results/{case}.genes.tsv")
    if not fs:
        return []
    with open(fs[0]) as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip()]
    hdr = [h.lstrip("#") for h in rows[0]]
    gi = hdr.index("GENE_SYMBOL")
    return list(dict.fromkeys(r[gi] for r in rows[1:]))  # one row per gene x MOI; keep first


if sys.argv[1] == "submit":
    model = sys.argv[2]
    sub = []
    for case in man:
        g = exomiser_genes(case)[:50]
        if not g:
            continue
        sub.append(dict(cohort="fu2022", case=case, genes=man[case]["genes"], findings=cases[case]["findings"],
                        prompt=("A fetus has the following findings on prenatal ultrasound:\n"
                                + "\n".join("- " + f for f in cases[case]["findings"])
                                + "\n\nChromosomal microarray was normal. Exome sequencing found rare candidate variants "
                                  "in the following genes (alphabetical order):\n" + ", ".join(sorted(g))
                                + "\n\nRank these candidate genes from most to least likely to be the causal gene for "
                                  "this fetus. Use only genes from the list, as HGNC symbols.")))
    json.dump(sub, open(f"{V}/rerank_cases.json", "w"))
    os.system(f"cd {B} && venv/bin/python scripts/claude_batch.py submit {V}/rerank_cases.json "
              f"v1_rerank_{model.replace('claude-', '')} {model} 1")
else:
    import importlib.util
    spec = importlib.util.spec_from_file_location("sc", f"{B}/scripts/score_lib.py")
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    out = {}
    for path in sorted(glob.glob(f"{B}/outputs/v1_rerank_*.jsonl")):
        tag = os.path.basename(path)[:-6]
        llm = {json.loads(l)["case"]: json.loads(l).get("genes") or [] for l in open(path)}
        res = []
        for case in man:
            ex = exomiser_genes(case)
            if not ex:
                continue
            causal = {sc.norm(g)[0] for g in man[case]["genes"]}
            ex_rank = next((i + 1 for i, g in enumerate(ex) if sc.norm(g)[0] in causal), 9999)
            top50 = [sc.norm(g)[0] for g in ex[:50]]
            lst = [x for x in dict.fromkeys(sc.norm(g)[0] for g in llm.get(case, [])) if x in top50]
            lst += [g for g in top50 if g not in lst]  # genes the LLM omitted keep Exomiser order at the end
            ll_rank = next((i + 1 for i, g in enumerate(lst) if g in causal), ex_rank) if ex_rank <= 50 else ex_rank
            fused = sorted(top50, key=lambda g: -(1 / (60 + top50.index(g) + 1) + 1 / (60 + lst.index(g) + 1)))
            fu_rank = next((i + 1 for i, g in enumerate(fused) if g in causal), ex_rank) if ex_rank <= 50 else ex_rank
            res.append((case, ex_rank, ll_rank, fu_rank))
        n = len(res)
        summ = {m: {f"top{t}": sum(r[i] <= t for r in res) for t in (1, 5, 10)} for i, m in
                [(1, "exomiser"), (2, "llm_rerank"), (3, "fusion")]}
        out[tag] = dict(n=n, causal_in_exomiser_top50=sum(r[1] <= 50 for r in res), summary=summ, per_case=res)
        print(tag, "n", n, "in top50", out[tag]["causal_in_exomiser_top50"], json.dumps(summ))
    json.dump(out, open(f"{B}/outputs/v1_results.json", "w"), indent=1)
