"""Build input variants for robustness tests (PLAN_v2). Each output is a cases JSON
with the same fetuses; 'findings' replaced, or a full 'prompt' given.
  N1 shuffled phenotype (5 permutations, donor fetus with a different causal gene)
  T3a order shuffled; T3b HPO exact synonyms; T3c HPO identifiers only;
  S2 HPO term labels (same input as Exomiser)
  T2 recall probe (citation + case number, no findings)"""
import csv, json, os, random, re, sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
cases = json.load(open(os.path.join(OUT, "..", "cases.json")))

# HPO id / labels per fetus, from the pre-cutoff extraction
hpo = {}
for r in csv.DictReader(open(f"{PROJ}/inputs/pd_hpo/cases.tsv"), delimiter="\t"):
    k = r["cohort"] + "|" + r["case"]
    hpo.setdefault(k, [])
    if r["hpo_id"] not in hpo[k]:
        hpo[k].append(r["hpo_id"])

# HPO 2026 labels and exact synonyms
name, syn, cur = {}, {}, None
for line in open(f"{PROJ}/inputs/hpo2026/hp.obo"):
    line = line.rstrip("\n")
    if line.startswith("id: HP:"):
        cur = line[4:]
    elif line.startswith("name: ") and cur:
        name[cur] = line[6:]
    elif line.startswith("synonym: ") and cur and " EXACT" in line:
        m = re.match(r'synonym: "(.+?)" EXACT', line)
        if m and "layperson" not in line.lower():
            syn.setdefault(cur, []).append(m.group(1))
    elif line == "[Term]":
        cur = None

rng = random.Random(20261030)
key = lambda c: c["cohort"] + "|" + str(c["case"])


def dump(tag, recs):
    json.dump(recs, open(os.path.join(OUT, f"{tag}.json"), "w"), indent=0)
    print(tag, len(recs))


# T3a order shuffled
dump("T3a_order", [dict(c, findings=rng.sample(c["findings"], len(c["findings"]))) for c in cases])
# S2 HPO labels
dump("S2_hpolabel", [dict(c, findings=[name.get(h, h) for h in hpo[key(c)]]) for c in cases])
# T3b synonyms (first exact synonym that differs from the label; label if none)
n_syn = 0
recs = []
for c in cases:
    f = []
    for h in hpo[key(c)]:
        s = [x for x in syn.get(h, []) if x.lower() != name.get(h, "").lower()]
        if s:
            n_syn += 1; f.append(rng.choice(s))
        else:
            f.append(name.get(h, h))
    recs.append(dict(c, findings=f))
dump("T3b_synonym", recs)
print("terms replaced by a synonym:", n_syn)
# T3c identifiers only
dump("T3c_hpoid", [dict(c, findings=hpo[key(c)]) for c in cases])
# N1 shuffled phenotype, 5 permutations
for p in range(1, 6):
    recs = []
    for c in cases:
        donors = [d for d in cases if not set(d["genes"]) & set(c["genes"])]
        d = rng.choice(donors)
        recs.append(dict(c, findings=d["findings"], donor=key(d)))
    dump(f"N1_shuffle{p}", recs)

# T2 recall probe
CIT = {
    "fu2022": "Fu F, et al. Application of exome sequencing for prenatal diagnosis of fetal structural anomalies: clinical experience and lessons learned from a cohort of 1618 fetuses. Genome Medicine 2022 (supplementary Table S3)",
    "smogavec2022": "Smogavec M, et al. Singleton exome sequencing of 90 fetuses with ultrasound anomalies revealing novel disease-causing variants and genotype-phenotype correlations. European Journal of Human Genetics 2022",
    "graham2026": "Graham et al. Inherited variants in autosomal dominant disease genes are a significant cause of fetal structural anomalies. Journal of Medical Genetics 2026",
    "aogs2026": "Yao et al. Prenatal exome sequencing of fetuses with central nervous system anomalies based on prenatal ultrasound and magnetic resonance imaging. Acta Obstetricia et Gynecologica Scandinavica 2026",
}
recs = []
for c in cases:
    p = (f"The following publication reports a cohort of fetuses with a monogenic diagnosis "
         f"on prenatal exome sequencing:\n{CIT[c['cohort']]}\n\n"
         f"In that publication, case (fetus) number {c['case']} received a monogenic diagnosis. "
         f"From your memory of this publication, list the 50 genes most likely to be the causal gene "
         f"for that specific case, ranked from most to least likely. Use HGNC gene symbols only.")
    recs.append(dict(c, prompt=p))
dump("T2_recall", recs)
