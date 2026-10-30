#!/bin/bash
B=$(cd "$(dirname "$0")/.." && pwd); cd $B; export OLLAMA_HOST=127.0.0.1:11555
for m in llama3.1:8b gemma3:12b qwen3:14b gpt-oss:20b; do
  while ! tools/ollama/bin/ollama list | grep -q "^$m "; do sleep 30; done
  tag=$(echo $m | tr ':.' '__')
  venv/bin/python scripts/run_llm.py work/cases.json $m outputs/open_${tag}.jsonl > logs/open_${tag}.log 2>&1
done
echo ALLDONE >> logs/open_done.log
