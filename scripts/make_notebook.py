"""Write reproduce.ipynb (Python 3.12 kernel)."""
import os
import nbformat as nbf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
    md("""# Reproduce: large language models for gene prioritisation from fetal ultrasound findings

Run All rebuilds every reported number from the committed inputs and model outputs, redraws the figures and compares
each regenerated file with the committed copy in `outputs/` and `work/`. It prints `REPRODUCED` when all agree.

* Hand-entered data: `inputs_manual/` (both extractions, adjudication log, final case table) and `inputs/pd_hpo/`
  (HPO coding of the pre-cutoff cohorts).
* Model answers are stored in `outputs/*.jsonl` and Exomiser results in `outputs/exomiser_2512*.json`,
  `v1/results/` and `v1p/results/`. Querying the models again is described at the end and is not part of Run All.
* Needs Python 3.12 (`requirements.txt`) and R with lme4. About 5 minutes on a laptop."""),
    code("""import json, os, shutil, subprocess, sys, tempfile
import pandas as pd
from IPython.display import Image, display
PY = sys.executable
def run(*args, out=None):
    r = subprocess.run(list(args), capture_output=True, text=True)
    if out:
        open(out, 'w').write(r.stdout + r.stderr)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:]); raise RuntimeError(' '.join(args))
    return r.stdout
subprocess.run(['bash', 'scripts/download.sh'], check=True)
# keep the committed results as the reference before anything is rebuilt
REF = tempfile.mkdtemp()
for d in ['outputs', 'work']:
    shutil.copytree(d, os.path.join(REF, d))
print('reference copy in', REF)"""),
    md("## 1. Case set\nOne record per fetus with findings as written, causal genes, HPO terms, Resnik rank (HPO 2026) and case features."),
    code("""run(PY, 'scripts/build_cases.py', 'inputs/pd_hpo/cases.tsv', 'inputs/pd_hpo/ranks.tsv', 'work/cases.json')
run(PY, 'scripts/resnik_full.py', 'work/resnik_top500.json')
run(PY, 'scripts/annot_gap.py', 'work/annot_gap.json')
print(run(PY, 'scripts/build_v2.py'))
run(PY, 'scripts/difficulty_features.py')
print(run(PY, 'scripts/derive_work.py'))"""),
    md("## 2. Prompt inputs for the robustness tests and retrieval arms\nThese files were sent to the models. Rebuilding them shows that the stored answers belong to these inputs."),
    code("""run(PY, 'scripts/make_variants.py', 'work/variants')
for a in 'ABC':
    run(PY, 'scripts/rag_build.py', 'dev', a, f'work/rag_dev_{a}.json')
run(PY, 'scripts/rag_build.py', 'test', 'A', 'work/rag_test_A.json');"""),
    md("## 3. Primary analysis: 153 fetuses reported from 1 July 2026"),
    code("""run(PY, 'scripts/analyze_primary.py', 'outputs/primary.json', out='outputs/primary.txt')
P = json.load(open('outputs/primary.json'))
display(pd.DataFrame(P['topk']).T)
pd.DataFrame(P['primary']).T"""),
    code("""run(PY, 'scripts/sens_hydrops.py', out='outputs/sens_hydrops.txt')
run(PY, 'scripts/score_open_post.py', out='outputs/open_post.txt')
print(open('outputs/sens_hydrops.txt').read(), open('outputs/open_post.txt').read())"""),
    md("## 4. Earlier against later fetuses: adjusted, matched and mixed-effects models"),
    code("""run(PY, 'scripts/adjusted.py', 'outputs/adjusted.json', out='outputs/adjusted.txt')
A = json.load(open('outputs/adjusted.json'))
display(pd.DataFrame({k: {'OR': v['adjusted']['OR'], 'CI': v['adjusted']['ci']} for k, v in A['models'].items()}).T)
pd.DataFrame(A['matched']).T"""),
    code("""run(PY, 'scripts/mixed_data.py')
run('Rscript', 'scripts/mixed.R', out='outputs/mixed.txt')
print(open('outputs/mixed.txt').read())"""),
    md("## 5. Robustness: recall probe, shuffled findings, rewording, replicates, invalid symbols"),
    code("""run(PY, 'scripts/analyze_v2.py', 'outputs/analysis_v2.json', out='outputs/analysis_v2.txt')
run(PY, 'scripts/compare_all.py', 'outputs/compare_all.tsv', out='outputs/compare_all.txt')
run(PY, 'scripts/t2_check.py', out='outputs/t2_check.txt')
claude = [f'outputs/{m}-5-5_r1.jsonl' for m in ('opus', 'sonnet', 'haiku')]
opens = [f'outputs/open_{t}.jsonl' for t in ('llama3_1_8b', 'gemma3_12b', 'qwen3_14b', 'gpt-oss_20b')]
run(PY, 'scripts/score.py', 'outputs/score_symbols.tsv', *claude, *opens)
V = json.load(open('outputs/analysis_v2.json'))
display(pd.DataFrame({k: v['all'] for k, v in V['topk'].items()}).T)
print(open('outputs/t2_check.txt').read())
pd.DataFrame(V['replicates']).T"""),
    md("## 6. Retrieval-augmented prompts"),
    code("""print(run(PY, 'scripts/rag_score.py', 'dev', out='outputs/rag_dev.txt') or open('outputs/rag_dev.txt').read())
run(PY, 'scripts/rag_score.py', 'test', 'A', out='outputs/rag_test.txt')
pd.DataFrame(json.load(open('outputs/rag_test.json'))).drop(['arm', 'n'], errors='ignore')"""),
    md("## 7. Clinical simulation: causal variants in benchmark exomes, Exomiser, LLM re-ranking"),
    code("""run(PY, 'scripts/v1_rerank.py', 'score', out='outputs/v1_results.txt')
run(PY, 'scripts/v1_stats.py', out='outputs/v1_stats.txt')
run(PY, 'scripts/v1p_rerank.py', 'score', out='outputs/v1p_results.txt')
R = json.load(open('outputs/v1p_results.json'))
pd.DataFrame({k: {**{f'exomiser_{t}': v['exomiser'][t] for t in ('top1', 'top10')},
                  **{f'llm_{t}': v['llm_rerank'][t] for t in ('top1', 'top10')},
                  **{f'fusion_{t}': v['fusion'][t] for t in ('top1', 'top10')}} for k, v in R.items()}).T"""),
    md("## 8. Figures"),
    code("""run(PY, 'scripts/fig_data.py')
run(PY, 'scripts/figures.py'); run(PY, 'scripts/figure1.py')
for i in range(1, 5):
    display(Image(f'docs/figures/figure{i}.png', width=900))"""),
    md("## 9. Comparison with the committed results"),
    code("""files = [os.path.join(d, f) for d in ['work', 'outputs'] for f in sorted(os.listdir(os.path.join(REF, d)))
         if os.path.isfile(os.path.join(REF, d, f)) and not f.endswith('.jsonl')]
files += [os.path.join('work/variants', f) for f in sorted(os.listdir(os.path.join(REF, 'work/variants')))]
r = subprocess.run([PY, 'scripts/compare_outputs.py', REF, '.', *files], capture_output=True, text=True)
print(r.stdout)
assert r.returncode == 0"""),
    md("""## Querying the models again (not run here)

The stored answers were produced on 30 October 2026. Re-running needs an Anthropic API key in `~/.anthropic_key`,
Ollama v0.40.13 with the model digests listed in the Supplementary Information, Exomiser 15.1.0 with data release
2512 and the Genome in a Bottle v4.2.1 call sets (set `GIAB_DIR` and `EXOMISER_DATA`). Claude models do not accept a
temperature setting, so new answers will differ from the stored ones to the extent shown by the three replicates.

* Claude, all prompts: `scripts/claude_batch.py submit <cases.json> <tag> <model> <rep>`, then `collect <tag>`
* Open-weight models: `scripts/run_open.sh`, `scripts/run_open_post.sh`
* Exomiser phenotype-only: `scripts/run_exomiser.py`
* Retrieval: `scripts/run_rag.sh`
* Clinical simulation: `scripts/run_v1.sh` (largest pre-cutoff cohort), `scripts/run_v1p.sh` (post-cutoff)"""),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "prenatal-llm", "display_name": "Python 3.12 (prenatal_llm_rank)", "language": "python"}})
nbf.write(nb, os.path.join(ROOT, "reproduce.ipynb"))
print("reproduce.ipynb written")
