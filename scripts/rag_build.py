"""Build RAG prompts (docs/PLAN_rag.md). usage: rag_build.py <dev|test> <A|B|C> <out.json>
Needs scripts/{rank.py,hpo.py}, inputs/hpo2026, cases_v2.json,
hpo_terms_v2.json, outputs/exomiser_2512*.json."""
import csv, json, os, sys
from functools import lru_cache
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv[3] = os.path.abspath(sys.argv[3])
sys.path.insert(0, f"{B}/scripts"); os.chdir(f"{B}/scripts")
from rank import KB

split, arm, out = sys.argv[1:4]
k26 = KB("2026", "2026")
cases = json.load(open(f"{B}/work/cases_v2.json"))
terms = json.load(open(f"{B}/work/hpo_terms_v2.json"))
exo = json.load(open(f"{B}/outputs/exomiser_2512.json"))["hiphive_all"]
exo.update(json.load(open(f"{B}/outputs/exomiser_2512_new.json"))["hiphive_all"])
key = lambda c: f"{c['cohort']}|{c['case']}"
PRE = [c for c in cases if c["period"] == "pre"]
TARGET = PRE if split == "dev" else [c for c in cases if c["period"] == "post"]

PA = k26.anc_desc_pa()
anc = {t: k26.anc[t] & PA for t in {t for v in terms.values() for t in v} if t in k26.anc}


@lru_cache(maxsize=None)
def mica(a, b):
    s = anc.get(a, set()) & anc.get(b, set())
    return max((k26.ic.get(t, 0.0) for t in s), default=0.0)


def bma(x, y):
    x = [t for t in x if t in anc]; y = [t for t in y if t in anc]
    if not x or not y:
        return 0.0
    f = sum(max(mica(*sorted((a, b))) for b in y) for a in x) / len(x)
    g = sum(max(mica(*sorted((a, b))) for a in x) for b in y) / len(y)
    return (f + g) / 2


# gene -> disorders (names) from phenotype.hpoa via genes_to_phenotype disease ids
dname = {}
for line in open(f"{B}/inputs/hpo2026/phenotype.hpoa"):
    if line.startswith("#") or line.startswith("database_id"):
        continue
    p = line.split("\t")
    dname.setdefault(p[0], p[1])
gdis = {}
with open(f"{B}/inputs/hpo2026/genes_to_phenotype.txt") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        gdis.setdefault(r["gene_symbol"], [])
        if r["disease_id"] not in gdis[r["gene_symbol"]]:
            gdis[r["gene_symbol"]].append(r["disease_id"])

BASE = ("A fetus has the following findings on prenatal ultrasound:\n{findings}\n\n"
        "Chromosomal microarray was normal. Exome sequencing identified a monogenic diagnosis.\n")
TAIL = ("\nThe retrieved information may or may not be relevant. You may also propose genes that are not listed.\n"
        "List the 50 genes most likely to be the causal gene, ranked from most to least likely. "
        "Use HGNC gene symbols only.")
recs = []
for c in TARGET:
    k = key(c)
    ctx = ""
    if arm in ("A", "C"):
        pool = [p for p in PRE if key(p) != k]
        sims = sorted(pool, key=lambda p: -bma(terms[k], terms[key(p)]))[:5]
        ctx += "\nRetrieved: published fetuses with the most similar prenatal findings\n" + "".join(
            f"- Findings: {'; '.join(p['findings'])}. Causal gene: {', '.join(p['genes'])}\n" for p in sims)
    if arm in ("B", "C"):
        gl = [g for g, _ in exo.get(k, [])][:20]
        lines = []
        for g in gl:
            ds = [dname.get(d, d) for d in gdis.get(g, [])][:2]
            lines.append(f"- {g}: {'; '.join(ds) if ds else 'no listed disorder'}")
        ctx += "\nRetrieved: top 20 candidate genes from phenotype-ontology matching (Exomiser), with associated disorders\n" + "\n".join(lines) + "\n"
    recs.append(dict(c, prompt=BASE.format(findings="\n".join("- " + f for f in c["findings"])) + ctx + TAIL))
json.dump(recs, open(out, "w"))
print(split, arm, len(recs), "example length", len(recs[0]["prompt"]))
