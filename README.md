# Prenatal LLM gene ranking

Code and data to reproduce the study *Large language models for gene prioritisation from fetal ultrasound findings*
(T.H.L. Tran).

The study gives the prenatal ultrasound findings of 452 fetuses with a monogenic diagnosis, taken from published
prenatal exome sequencing cohorts, to three Claude models and four open-weight models, and compares the rank of the
causal gene with Exomiser and HPO semantic similarity. The primary analysis uses the 153 fetuses reported from 1 July
2026, after the training data cutoff of the models. Robustness tests (recall probe, shuffled findings, rewording),
retrieval-augmented prompts and a clinical simulation with causal variants injected into benchmark exomes follow.
All data are public and de-identified.

## Quick start

```bash
git clone https://github.com/huulocmedvnu/prenatal-llm-ranking.git
cd prenatal-llm-ranking
pip install -r requirements.txt          # Python 3.12; R with lme4 for the mixed models
python -m ipykernel install --user --name prenatal-llm
jupyter lab reproduce.ipynb               # Kernel > Restart Kernel and Run All Cells
```

The notebook downloads the 2026 and 2020 HPO releases, rebuilds the case set and every analysis from the stored model
answers, redraws the figures and compares each regenerated file with the committed copy. It prints `REPRODUCED` when
all agree. A run takes about 5 minutes on a laptop. The mixed-model output was produced with R 4.3.3 and lme4 2.1.0;
other lme4 versions agree within the stated tolerance.

Querying the models again is not part of Run All. The last cell of the notebook lists the scripts and what they need
(an Anthropic API key, Ollama, Exomiser 15.1.0 with data release 2512, Genome in a Bottle v4.2.1 call sets).

## Pipeline

| Script | What it does |
|---|---|
| `download.sh` | HPO release v2026-09-01 and the 2020-10-12 release (PyHPO 2.5.0 package data) |
| `adjudicate.py`, `build_cases.py`, `build_v2.py`, `derive_work.py` | Case set from the two extractions and the earlier HPO coding |
| `resnik_full.py`, `annot_gap.py`, `difficulty_features.py` | HPO semantic similarity ranks, annotation of findings, case features |
| `claude_batch.py`, `run_llm.py`, `run_exomiser.py` | Model queries (Claude Message Batches, Ollama) and phenotype-only Exomiser |
| `analyze_primary.py`, `sens_hydrops.py`, `score_open_post.py` | Primary analysis and sensitivity analyses |
| `adjusted.py`, `mixed_data.py`, `mixed.R` | Period comparison: adjusted, propensity-matched and mixed-effects models |
| `make_variants.py`, `analyze_v2.py`, `t2_check.py`, `score.py`, `compare_all.py` | Robustness tests |
| `rag_build.py`, `rag_score.py` | Retrieval-augmented prompts |
| `v1_*.py`, `v1p_*.py` | Clinical simulation (variant injection, Exomiser, LLM re-ranking, rank fusion) |
| `fig_data.py`, `figures.py`, `figure1.py` | Figures |

The analysis plans are in `docs/PLAN.md`, `docs/PLAN_v2.md` and `docs/PLAN_rag.md`, with the extraction rules in
`docs/extract_instructions.md`. Analyses added after a plan was fixed are marked post hoc there.

## Data

| Path | Content |
|---|---|
| `inputs_manual/v2_extraction_A/`, `v2_extraction_B/` | Two independent extractions of the post-cutoff publications |
| `inputs_manual/v2_adjudication.csv`, `v2_cases.csv` | Adjudication log and final post-cutoff case table with variants |
| `inputs/pd_hpo/` | HPO coding and HPO 2026 ranks of the pre-cutoff cohorts |
| `data/` | HGNC complete set used for symbol mapping, causal variants of the largest pre-cutoff cohort in GRCh38 |
| `outputs/*.jsonl` | Every model answer, with batch identifiers in `outputs/batches.jsonl` |
| `outputs/exomiser_2512*.json`, `v1*/results/` | Exomiser results (phenotype only, and with variants) |
| `outputs/`, `work/` | Every reported number and the intermediate files |

Only per-fetus findings, gene symbols and variants from the published tables of the source studies are included.
The source publications are cited in the paper.

## Contact

Tran Thai Huu Loc, MD, Department of Obstetrics and Gynaecology, Hong Hung Hospital, Tay Ninh City, Viet Nam.
ORCID 0009-0009-1810-010X. tranthaihuuloc2@gmail.com
