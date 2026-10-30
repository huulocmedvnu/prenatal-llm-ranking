"""Score RAG runs. usage: rag_score.py dev  -> prints top-10 per arm, writes outputs/rag_dev_choice.txt
                     rag_score.py test <arm> -> primary RAG comparison, writes outputs/rag_test.json"""
import os, json, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mode = sys.argv[1]
argv = sys.argv; sys.argv = ["x", "/dev/null"]
exec(open(f"{B}/scripts/analyze_primary.py").read().split("res = {")[0]); sys.argv = argv
O = f"{B}/outputs"
PRE = [k for k, c in CASE.items() if c["period"] == "pre"]
if mode == "dev":
    res = {}
    for arm in "ABC":
        r = llm([f"{O}/rag_dev_{arm}_opus.jsonl"])
        res[arm] = sum(r[k] <= 10 for k in PRE)
    plain = sum(R["opus_r1"][k] <= 10 for k in PRE)
    best = max("ABC", key=lambda a: (res[a], -"ABC".index(a)))
    print("dev (n=%d) top-10: plain Opus %d, " % (len(PRE), plain) + ", ".join(f"{a} {v}" for a, v in res.items()), "-> chosen", best)
    open(f"{O}/rag_dev_choice.txt", "w").write(best)
else:
    arm = sys.argv[2]; out = {"arm": arm, "n": len(POST)}
    ref_exo = [R["exomiser_hiphive"][k] <= 10 for k in POST]
    for m in ["opus", "sonnet", "haiku"]:
        r = llm([f"{O}/rag_test_{arm}_{m}.jsonl"])
        a = [r[k] <= 10 for k in POST]
        d, lo, hi, p, b, c = newcombe(a, [R[f"{m}_r1"][k] <= 10 for k in POST])
        de, loe, hie, pe, _, _ = newcombe(a, ref_exo)
        out[m] = dict(top1=sum(r[k] <= 1 for k in POST), top10=sum(a), top50=sum(r[k] <= 50 for k in POST),
                      plain_top10=sum(R[f"{m}_r1"][k] <= 10 for k in POST),
                      vs_plain=dict(diff=round(d, 1), ci=[round(lo, 1), round(hi, 1)], p=p, gain=b, loss=c),
                      vs_exomiser=dict(diff=round(de, 1), ci=[round(loe, 1), round(hie, 1)], p=pe))
        print(m, json.dumps(out[m]))
    json.dump(out, open(f"{O}/rag_test.json", "w"), indent=1, default=float)
