#!/bin/bash
# Chained runner (tmux): wait for the post-cutoff batches and Exomiser, then run the primary analysis.
B=$(cd "$(dirname "$0")/.." && pwd); cd $B
for t in opus-5-5_new_r1 opus-5-5_new_r2 opus-5-5_new_r3 sonnet-5-5_new_r1 haiku-5-5_new_r1; do
  until venv/bin/python scripts/claude_batch.py collect $t >> logs/primary_runner.log 2>&1; do sleep 120; done
done
until [ -s outputs/exomiser_2512_new.json ]; do sleep 30; done
venv/bin/python scripts/analyze_primary.py outputs/primary.json > outputs/primary.txt 2>&1
echo PRIMARY_DONE >> logs/primary_runner.log
