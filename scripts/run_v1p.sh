#!/bin/bash
# V1 on post-cutoff fetuses: resolve -> inject -> Exomiser (parallel) -> LLM re-rank -> score
set -x
B=$(cd "$(dirname "$0")/.." && pwd); cd $B; P=venv/bin/python; E=$B/tools/exomiser/exomiser-cli-15.1.0
$P scripts/v1p_prepare.py
mkdir -p $B/v1p/results; rm -f $B/v1p/chunk_*
split -n l/4 -d $B/v1p/batch.txt $B/v1p/chunk_
for c in $B/v1p/chunk_*; do (cd $E && java -Xmx12g -jar exomiser-cli-15.1.0.jar batch $c) > logs/v1p_exomiser_$(basename $c).log 2>&1 & done
wait
: > $B/v1p/batch_retry.txt
while read l; do f=$(echo "$l" | sed 's/.*--output-filename //'); [ -s $B/v1p/results/$f.genes.tsv ] || echo "$l" >> $B/v1p/batch_retry.txt; done < $B/v1p/batch.txt
[ -s $B/v1p/batch_retry.txt ] && (cd $E && java -Xmx24g -jar exomiser-cli-15.1.0.jar batch $B/v1p/batch_retry.txt) > logs/v1p_exomiser_retry.log 2>&1
for m in claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5; do $P scripts/v1p_rerank.py submit $m; done
for m in opus-5-5 sonnet-5-5 haiku-5-5; do until $P scripts/claude_batch.py collect v1p_rerank_$m; do sleep 120; done; done
$P scripts/v1p_rerank.py score > outputs/v1p_results.txt 2>&1
echo V1P_DONE
