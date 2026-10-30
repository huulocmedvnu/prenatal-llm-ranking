# Prenatal LLM gene ranking: go/no-go plan

Fixed 2026-10-30, before any model output was generated.

## Question
Do large language models rank the causal gene higher than HPO semantic
similarity (Resnik best-match average, HPO 2026 release) when given only
fetal ultrasound findings?

## Data
335 fetuses with a monogenic diagnosis from four published cohorts, as
extracted for an earlier HPO study (cases.tsv, ranks.tsv).
- Before the training cutoff of the open models: Fu 2022 (229),
  Smogavec 2022 (31).
- After it: Graham 2026 (J Med Genet, 20 Apr 2026, 39),
  Yao 2026 (AOGS, 2 Jul 2026, 36).

## Models (local, local workstation, RTX 3080, Ollama v0.40.13, temperature 0, seed 1)
llama3.1:8b, gemma3:12b, qwen3:14b, gpt-oss:20b.
All four were released before April 2026.

## Prompt
Finding labels as written in the source (not HPO identifiers), a statement
that the findings come from prenatal ultrasound in a fetus with a
monogenic diagnosis after normal microarray, and a request for the 50
most likely genes as a ranked JSON array of HGNC symbols.

## Scoring
- Symbols are mapped to approved HGNC symbols via previous symbols and
  aliases.
- Rank = position of the first causal gene, otherwise >50.
- Invalid symbols (not in HGNC) are counted as hallucinations.

## Outcomes
- Primary: top-10 proportion, LLM vs Resnik 2026 on the same fetuses,
  exact McNemar. Reported separately for pre-cutoff (260) and
  post-cutoff (75) fetuses.
- Secondary: top-1, top-5, top-50, parse failure rate, hallucination
  rate, and reciprocal rank fusion of LLM and Resnik.

## Gate
GO if all of the following hold:
1. Parse success is at least 95% for at least two models.
2. For the best model, the post-cutoff top-10 proportion is at least
   the Resnik proportion in the same fetuses, OR rank fusion raises the
   top-10 proportion over Resnik by at least 5 percentage points in all
   335 fetuses.
3. Hallucinated symbols are under 10% of returned symbols.

NO-GO otherwise, unless pre-cutoff performance is high and post-cutoff
performance is low. That pattern would itself be a memorisation finding,
and it would be reported as an alternative framing.

The gate uses only open models. Commercial models (GPT, Claude, Gemini)
are for the full study and need API keys.
