"""Submit / collect Message Batches: one request per fetus x model x replicate.
usage: claude_batch.py submit <cases.json> <tag> <model> <rep>
       claude_batch.py collect <tag>        (writes outputs/<tag>.jsonl when ended)"""
import json, os, sys, time
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client = anthropic.Anthropic(api_key=open(os.path.expanduser("~/.anthropic_key")).read().strip())

SYSTEM = "You are a clinical geneticist specialising in prenatal diagnosis."
TEMPLATE = (
    "A fetus has the following findings on prenatal ultrasound:\n{findings}\n\n"
    "Chromosomal microarray was normal. Exome sequencing identified a "
    "monogenic diagnosis.\n"
    "List the 50 genes most likely to be the causal gene, ranked from most "
    "to least likely. Use HGNC gene symbols only."
)
SCHEMA = {"type": "object",
          "properties": {"genes": {"type": "array", "items": {"type": "string"}}},
          "required": ["genes"], "additionalProperties": False}


def submit(cases_json, tag, model, rep):
    cases = json.load(open(cases_json))
    reqs = []
    for i, c in enumerate(cases):
        cid = f"f{i}_r{rep}"
        reqs.append(Request(custom_id=cid, params=MessageCreateParamsNonStreaming(
            model=model, max_tokens=16000, system=SYSTEM,
            messages=[{"role": "user", "content": c.get("prompt") or TEMPLATE.format(
                findings="\n".join("- " + f for f in c["findings"]))}],
            output_config={"effort": "medium",
                           "format": {"type": "json_schema", "schema": SCHEMA}})))
    b = client.messages.batches.create(requests=reqs)
    meta = {"tag": tag, "model": model, "rep": rep, "batch_id": b.id, "cases": os.path.abspath(cases_json),
            "n": len(reqs), "submitted": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open(f"{B}/outputs/batches.jsonl", "a") as f:
        f.write(json.dumps(meta) + "\n")
    print(json.dumps(meta))


def collect(tag):
    metas = [json.loads(l) for l in open(f"{B}/outputs/batches.jsonl")]
    m = [x for x in metas if x["tag"] == tag][-1]
    cases = json.load(open(m.get("cases", f"{B}/work/cases.json")))
    b = client.messages.batches.retrieve(m["batch_id"])
    print(tag, b.processing_status, b.request_counts)
    if b.processing_status != "ended":
        return False
    out = open(f"{B}/outputs/{tag}.jsonl", "w")
    for r in client.messages.batches.results(m["batch_id"]):
        i, rep = r.custom_id[1:].split("_r")
        c = cases[int(i)]
        rec = {"cohort": c["cohort"], "case": c["case"], "rep": int(rep), "model": m["model"],
               "status": r.result.type, "genes": None}
        if r.result.type == "succeeded":
            msg = r.result.message
            rec["stop"] = msg.stop_reason
            rec["usage"] = [msg.usage.input_tokens, msg.usage.output_tokens]
            txt = next((x.text for x in msg.content if x.type == "text"), "")
            rec["raw"] = txt
            try:
                rec["genes"] = json.loads(txt)["genes"]
            except Exception:
                pass
        out.write(json.dumps(rec) + "\n")
    out.close()
    return True


if __name__ == "__main__":
    if sys.argv[1] == "submit":
        submit(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
    else:
        sys.exit(0 if collect(sys.argv[2]) else 1)
