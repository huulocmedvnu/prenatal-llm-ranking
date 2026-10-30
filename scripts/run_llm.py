"""Ask a local Ollama model for a ranked gene list per fetus. Resumable."""
import json, os, sys, time, urllib.request

cases_json, model, out = sys.argv[1:4]
HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11555")

SYSTEM = "You are a clinical geneticist specialising in prenatal diagnosis."
TEMPLATE = (
    "A fetus has the following findings on prenatal ultrasound:\n{findings}\n\n"
    "Chromosomal microarray was normal. Exome sequencing identified a "
    "monogenic diagnosis.\n"
    "List the 50 genes most likely to be the causal gene, ranked from most "
    "to least likely. Use HGNC gene symbols only.\n"
    'Return JSON of the form {{"genes": ["SYMBOL1", "SYMBOL2", ...]}}.'
)
SCHEMA = {"type": "object",
          "properties": {"genes": {"type": "array", "items": {"type": "string"}, "maxItems": 50}},
          "required": ["genes"]}


def ask(findings):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": TEMPLATE.format(
                findings="\n".join("- " + f for f in findings))},
        ],
        "format": SCHEMA,
        "stream": False,
        "options": {"temperature": 0, "seed": 1, "num_ctx": 8192,
                    "num_predict": 3000},
    }
    if model.startswith("qwen3"):
        body["think"] = False
    if model.startswith("gpt-oss"):
        body["think"] = "low"
    req = urllib.request.Request(f"http://{HOST}/api/chat",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        res = json.load(r)
    return res["message"]["content"], time.time() - t


done = set()
if os.path.exists(out):
    for line in open(out):
        d = json.loads(line)
        done.add((d["cohort"], d["case"]))

cases = json.load(open(cases_json))
with open(out, "a") as fo:
    for c in cases:
        k = (c["cohort"], c["case"])
        if k in done:
            continue
        try:
            txt, sec = ask(c["findings"])
            err = None
        except Exception as e:  # keep going, record failure
            txt, sec, err = "", 0, repr(e)
        try:
            genes = json.loads(txt)["genes"]
        except Exception:  # truncated JSON: keep the symbols already written
            import re
            genes = re.findall(r'"([A-Za-z0-9][A-Za-z0-9\-\.]{0,19})"', txt.split("[", 1)[-1]) or None
        fo.write(json.dumps({"cohort": c["cohort"], "case": c["case"],
                             "model": model, "raw": txt, "genes": genes,
                             "sec": round(sec, 1), "error": err}) + "\n")
        fo.flush()
        print(model, k, "ok" if genes else "FAIL", round(sec, 1), flush=True)
