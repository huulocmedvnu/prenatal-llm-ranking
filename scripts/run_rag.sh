#!/bin/bash
# RAG chained runner (tmux), docs/PLAN_rag.md
set -x
B=$(cd "$(dirname "$0")/.." && pwd); cd $B; P=venv/bin/python
for a in A B C; do $P scripts/rag_build.py dev $a work/rag_dev_$a.json; done
for a in A B C; do $P scripts/claude_batch.py submit work/rag_dev_$a.json rag_dev_${a}_opus claude-opus-5-5 1; done
for a in A B C; do until $P scripts/claude_batch.py collect rag_dev_${a}_opus; do sleep 120; done; done
$P scripts/rag_score.py dev
ARM=$(cat outputs/rag_dev_choice.txt)
$P scripts/rag_build.py test $ARM work/rag_test_$ARM.json
for m in opus sonnet haiku; do $P scripts/claude_batch.py submit work/rag_test_$ARM.json rag_test_${ARM}_$m claude-$m-5-5 1; done
for m in opus sonnet haiku; do until $P scripts/claude_batch.py collect rag_test_${ARM}_$m; do sleep 120; done; done
$P scripts/rag_score.py test $ARM
echo RAG_DONE
