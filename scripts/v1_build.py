"""V1 clinical simulation inputs: for each Fu 2022 fetus whose causal variant(s) all resolved
to GRCh38, inject them into the GIAB HG005 (Han Chinese) coding-region background and write a
phenopacket. Zygosity: Het -> 0/1, Hom -> 1/1, Hemi -> 1. Background records at the injected
positions are removed. Writes v1/<case>.vcf.gz, v1/<case>.yml, v1/batch.txt, v1/manifest.json"""
import csv, gzip, json, os, subprocess
from collections import defaultdict

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{B}/v1"; os.makedirs(OUT, exist_ok=True)
BG = os.path.join(os.environ["GIAB_DIR"], "HG005.cds.vcf.gz")
EXO = f"{B}/tools/exomiser/exomiser-cli-15.1.0"
terms = json.load(open(f"{B}/work/hpo_terms_v2.json"))
sex = {}
for r in csv.DictReader(open(f"{B}/data/fu_s3_variants.tsv"), delimiter="\t"):
    if r["Gender"]:
        sex[r["Case ID"]] = r["Gender"].strip().lower()
var = defaultdict(list)
for r in csv.DictReader(open(f"{B}/data/fu_variants_grch38.tsv"), delimiter="\t"):
    var[r["case"]].append(r)

header, body = [], []
with gzip.open(BG, "rt") as f:
    for line in f:
        (header if line.startswith("#") else body).append(line)
sample = header[-1].rstrip("\n").split("\t")[-1]
manifest, batch = {}, []
for case, vs in var.items():
    if any(not v["chrom"] for v in vs) or f"fu2022|{case}" not in terms:
        continue
    inj = {}
    for v in vs:
        z = v["zygosity"].strip().lower()
        gt = "1/1" if z.startswith("hom") else "1" if z.startswith("hemi") else "0/1"
        if gt == "1" and v["chrom"] != "X":
            gt = "1/1"
        inj[(v["chrom"], int(v["pos"]))] = f"{v['chrom']}\t{v['pos']}\t.\t{v['ref']}\t{v['alt']}\t50\tPASS\t.\tGT\t{gt}\n"
    rec = [l for l in body if (l.split("\t", 2)[0].replace("chr", ""), int(l.split("\t", 2)[1])) not in inj]
    chrom_prefix = "chr" if body[0].startswith("chr") else ""
    rec += [chrom_prefix + l for l in inj.values()]
    order = {c: i for i, c in enumerate([str(i) for i in range(1, 23)] + ["X", "Y", "MT"])}
    rec.sort(key=lambda l: (order.get(l.split("\t")[0].replace("chr", ""), 99), int(l.split("\t")[1])))
    p = f"{OUT}/{case}.vcf"
    with open(p, "w") as f:
        f.writelines(header[:-1] + ['##INFO=<ID=SIM,Number=0,Type=Flag,Description="injected">\n', header[-1]])
        f.writelines(rec)
    subprocess.run(["bgzip", "-f", p], check=True); subprocess.run(["tabix", "-f", "-p", "vcf", p + ".gz"], check=True)
    s = "FEMALE" if sex.get(case, "").startswith("f") else "MALE" if sex.get(case, "").startswith("m") else "UNKNOWN_SEX"
    feats = "".join(f"  - type:\n      id: {t}\n" for t in terms[f"fu2022|{case}"])
    open(f"{OUT}/{case}.yml", "w").write(
        f"---\nid: {sample}\nsubject:\n  id: {sample}\n  sex: {s}\nphenotypicFeatures:\n{feats}"
        f"metaData:\n  createdBy: v1_build\n  phenopacketSchemaVersion: 1.0\n")
    batch.append(f"--sample {OUT}/{case}.yml --vcf {OUT}/{case}.vcf.gz --assembly hg38 --preset exome "
                 f"--output-format TSV_GENE,TSV_VARIANT --output-directory {OUT}/results --output-filename {case}")
    manifest[case] = {"genes": sorted({v["gene"] for v in vs if v["gene"]}), "variants": [v["hgvs"] for v in vs], "sex": s}
open(f"{OUT}/batch.txt", "w").write("\n".join(batch) + "\n")
json.dump(manifest, open(f"{OUT}/manifest.json", "w"), indent=1)
print("fetuses simulated", len(manifest), "of", len(var))
