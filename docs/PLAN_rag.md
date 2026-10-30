# Retrieval-augmented prompting (RAG): plan

Fixed 2026-10-30, before any RAG output was generated.

## Question
Does adding retrieved knowledge to the prompt raise the top-10 proportion of the causal gene
from fetal findings, in fetuses published after the model training cutoff?

## Arms
The base prompt is identical to the primary prompt. It is followed by retrieved context and
the sentence: "The retrieved information may or may not be relevant. You may also propose
genes that are not listed."

- **A, similar cases:**
  - The 5 knowledge-base fetuses with the highest phenotypic similarity.
  - Similarity is symmetric Resnik best-match average on HPO 2026 terms.
  - Each case is shown as its findings and causal gene.
- **B, ontology candidates:**
  - Exomiser hiPHIVE (phenotype-only) top-20 genes.
  - Each gene comes with up to 2 associated disorders from HPO phenotype.hpoa.
- **C:** A + B.

## Knowledge base and leakage control
- **Development:** the 299 pre-cutoff fetuses. Each fetus retrieves from the other pre-cutoff
  fetuses, never itself (leave-one-fetus-out).
- **Test:** the 153 post-cutoff fetuses. Retrieval uses the 299 pre-cutoff fetuses only.

## Selection and test
- On development, Claude Opus 5.5 is run once per arm.
- The arm with the highest top-10 count is selected. If two arms tie, the simpler arm (A or B
  before C) is selected.
- Only the selected arm is run on the test set, once each for Opus, Sonnet and Haiku.

## Endpoints
- **Primary:** top-10 on the 153 test fetuses, selected-arm Opus vs plain Opus (replicate 1),
  exact McNemar test, Newcombe CI.
- **Secondary:**
  - the same comparison for Sonnet and Haiku;
  - RAG Opus vs Exomiser;
  - top-1 and top-50.
