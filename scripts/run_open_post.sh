#!/bin/bash
# open-weight models on the 117 new post-cutoff fetuses
B=$(cd "$(dirname "$0")/.." && pwd); cd $B; export OLLAMA_HOST=127.0.0.1:11555
for m in qwen3:14b gpt-oss:20b gemma3:12b llama3.1:8b; do tag=$(echo $m | tr ":." "__"); venv/bin/python scripts/run_llm.py work/cases_v2_new.json $m outputs/open_new_${tag}.jsonl > logs/open_new_${tag}.log 2>&1; done
echo OPEN_NEW_DONE >> logs/open_new_done.log
