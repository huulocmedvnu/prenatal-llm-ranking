import sys, json
sys.argv=["x","/dev/null"]; exec(open("scripts/analyze_primary.py").read().split("res = {")[0])
import glob
tags=[t for t in ["qwen3_14b","gpt-oss_20b","gemma3_12b","llama3_1_8b"] if glob.glob(f"outputs/open_new_{t}.jsonl")]
ref=[R["exomiser_hiphive"][k]<=10 for k in POST]
for t in tags:
    paths=[f"outputs/open_{t}.jsonl", f"outputs/open_new_{t}.jsonl"]
    r=llm(paths); ks=[k for k in POST if k in r]
    if len(ks)<len(POST): print(t,"incomplete",len(ks)); continue
    a=[r[k]<=10 for k in POST]; d,lo,hi,p,b,c=newcombe(a,ref)
    print(t,"post n",len(POST),"top1",sum(r[k]<=1 for k in POST),"top10",sum(a),"(%.1f%%)"%(100*sum(a)/len(POST)),"vs exomiser diff %.1f [%.1f, %.1f] p %.2g"%(d,lo,hi,p))
