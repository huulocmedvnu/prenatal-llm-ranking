# Prenatal LLM gene ranking: confirmatory study plan (v2)

Fixed 2026-10-30. Supersedes the go/no-go plan (PLAN.md), whose results are
treated as exploratory. All analyses below are run with code committed before
the new outputs are generated. Target journal: European Journal of Human Genetics.

## Claim to be tested
From fetal ultrasound findings alone, general-purpose large language models rank
the causal gene higher than ontology-based prioritisation (Exomiser hiPHIVE
phenotype-only, Resnik/HPO), and the gain is concentrated where HPO gene
annotations lack the fetal findings.

## Threats and the control for each

| Threat | Control |
|---|---|
| Memorisation of published cases | T1 temporal hold-out; T2 recall probe; T3 perturbation; T4 post-cutoff gene discoveries |
| LLM only lists common prenatal genes | B1 popularity baseline; B2 organ-system baseline; N1 shuffled-phenotype null |
| Unfair comparator | Exomiser 15.1.0 at its best mode; identical HPO input given to LLM (S2) |
| Prompt fishing | Primary prompt fixed before any output; alternative prompts secondary only |
| Stochastic output | 3 replicates per model; agreement reported |
| Wrong ground truth | Sensitivity without uncertain diagnoses; ClinGen validity of causal genes |
| Clustering (same gene in many fetuses) | Gene-cluster bootstrap; mixed model with gene random effect |
| Single proprietary vendor | Open-weight models (local + 70B+ via API) |
| Phenotype-only is not the clinical task | V1 variant-level simulation in real exome backgrounds |

## Data
- Current: 335 fetuses, 4 cohorts (Fu 2022, Smogavec 2022, Graham 2026, Yao 2026).
- Expansion (before running confirmatory analyses): published prenatal exome
  cohorts with per-fetus ultrasound findings and causal gene. Priority to
  publications dated after 2026-06-30 (post-cutoff for all models). Same double
  extraction and reconciliation as the earlier extraction.
- Target: at least 150 post-cutoff fetuses.

## Methods compared
- LLMs: Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 (Batch API, effort medium,
  structured output); open-weight Llama 3.1 8B, Gemma 3 12B, Qwen3 14B,
  gpt-oss 20B (local); one 70B+ open model via API.
- Ontology: Exomiser 15.1.0 hiPHIVE (all species and human only), data 2512;
  Resnik best-match average, HPO v2026-09-01.
- Baselines:
  - B1 popularity: genes ranked by number of diagnoses in all other cohorts
    (leave-cohort-out), ignoring phenotype.
  - B2 organ-system popularity: same, restricted to fetuses with the same
    primary organ system.
  - N1 shuffled phenotype: each fetus's findings replaced by those of a random
    fetus with a different causal gene (5 permutations); LLM run on these.

## Primary endpoint and test
- Proportion of fetuses whose causal gene ranks in the top 10.
- Primary comparison: best Claude model (chosen on the go/no-go set) vs Exomiser
  hiPHIVE, in post-cutoff fetuses, exact McNemar.
- Effect size: paired difference with Newcombe 95% CI.
- Holm correction across the LLM vs Exomiser comparisons.

## Secondary analyses
1. Top-1, top-5, top-50, median rank, mean reciprocal rank.
2. All fetuses, and pre- vs post-cutoff (interaction test).
3. T2 recall probe: give citation + case number only and ask for the gene.
   Accuracy above chance indicates memorisation of that cohort.
4. T3 perturbation: findings shuffled in order, rewritten as synonyms, or given
   as HPO identifiers only. Stable performance argues against string recall.
5. T4 genes whose first disease association was published after 2025:
   expected failure, reported as a knowledge limit.
6. Annotation-gap stratification: fetuses in which none, some or all findings are
   annotated to the causal gene in HPO 2026 (earlier extraction). Hypothesis: the LLM
   advantage is largest when none are annotated.
7. Strata: organ system, number of findings, inheritance, cohort.
8. Mixed-effects logistic regression (top-10 ~ method + (1|fetus) + (1|gene)).
9. Replicate agreement (Fleiss kappa on top-10, rank correlation).
10. Hallucinated symbol rate; parse failures.
11. Rank fusion of LLM and Exomiser.

## V1 clinical simulation (key robustness test)
- For fetuses with a reported causal variant (HGVS, genome coordinates):
  - inject the variant(s) into a real exome background (1000 Genomes high
    coverage, matched ancestry where possible, de novo or inherited per
    the source);
  - run Exomiser with variants + phenotype;
  - re-rank Exomiser's top 50 candidates with the LLM given the same findings.
- Endpoint: rank of the causal variant, Exomiser alone vs Exomiser + LLM re-rank.
- This answers whether the LLM gain survives once variant evidence is present.

## Decision rules (stated in advance)
- The claim is supported if the primary comparison is significant after Holm
  correction and the lower bound of the paired-difference 95% CI is above 0.
- If B1/B2 popularity baselines reach within 5 points of the LLM, the claim is
  restated as "LLMs encode prenatal gene frequency", not phenotype reasoning.
- If T2 recall is above 5% for a cohort, that cohort is excluded from the
  primary analysis for that model.
- If V1 shows no gain with variants present, the paper reports phenotype-only
  benefit only and states the clinical limitation.

## Reproducibility
- Exact model IDs, dates of batches, batch IDs, prompts, schemas, raw outputs.
- Open-weight results with Ollama version and model digests.
- Code and extracted data released (public mirror, as for the earlier extraction).
