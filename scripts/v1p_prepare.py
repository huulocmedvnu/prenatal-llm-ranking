"""V1 on post-cutoff fetuses with reported variants (PLAN_v2, clinical simulation).
1. Resolve HGVS to GRCh38: with a RefSeq transcript -> VariantValidator; without -> Ensembl
   canonical transcript of the gene -> Ensembl variant_recoder. Genomic g. deletions are skipped.
2. Inject into a GIAB coding-region background (HG005 Han Chinese for cohorts from China,
   HG002 otherwise), write phenopackets and the Exomiser batch file.
Outputs in v1p/: <id>.vcf.gz, <id>.yml, batch.txt, manifest.json, resolve.tsv"""
import csv, gzip, json, os, re, subprocess, sys, time, urllib.parse, urllib.request

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f"{B}/v1p"; os.makedirs(OUT, exist_ok=True)
G = os.environ["GIAB_DIR"]
CHINA = {"frontgen_wes_us", "frontgen_ep300", "jcla_karyo_wes"}
terms = json.load(open(f"{B}/work/hpo_terms_v2.json"))
rows = list(csv.DictReader(open(f"{B}/inputs_manual/v2_cases.csv")))


def get(url, accept=True):
    req = urllib.request.Request(url, headers={"Accept": "application/json"} if accept else {})
    for t in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as f:
                return json.load(f)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                return None
            time.sleep(5 * (t + 1))
        except Exception:
            time.sleep(5 * (t + 1))
    return None


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    for t in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as f:
                return json.load(f)
        except Exception as e:
            print("post retry", t, e, flush=True); time.sleep(5 * (t + 1))
    return None


canon = {}
genes_all = sorted({g.strip() for r in rows for g in r["genes"].split(";") if g.strip()})
for i in range(0, len(genes_all), 200):
    d = post("https://rest.ensembl.org/lookup/symbol/homo_sapiens", {"symbols": genes_all[i:i + 200]}) or {}
    for g, v in d.items():
        canon[g] = (v or {}).get("canonical_transcript", "").split(".")[0] or None
print("canonical transcripts", sum(1 for v in canon.values() if v), "of", len(genes_all), flush=True)
recoded = {}
ids = []
for r in rows:
    if r["cohort"] == "uog_odyssey" or r["transcript"].startswith(("NM_", "NR_")):
        continue
    gs = [g.strip() for g in r["genes"].split(";") if g.strip()]
    for i, h in enumerate(h.strip() for h in r["hgvs_c"].split(";")):
        h = re.sub(r"\s+", "", h); g = gs[i] if i < len(gs) else (gs[0] if gs else "")
        if re.match(r"^[cn]\.", h) and canon.get(g):
            ids.append(f"{canon[g]}:{h}")
ids = sorted(set(ids))
for i in range(0, len(ids), 100):
    d = post("https://rest.ensembl.org/variant_recoder/human?vcf_string=1", {"ids": ids[i:i + 100]}) or []
    for item in d:
        for allele, v in item.items():
            if isinstance(v, dict) and v.get("input"):
                for vs in v.get("vcf_string", []):
                    m = re.match(r"^(\d+|X|Y)-(\d+)-([ACGTN]+)-([ACGTN]+)$", vs)
                    if m:
                        recoded.setdefault(v["input"], m.groups())

# one invalid id makes the batch POST fail with 400, so resolve the rest one by one in parallel
from concurrent.futures import ThreadPoolExecutor


def one(i):
    d = get("https://rest.ensembl.org/variant_recoder/human/" + urllib.parse.quote(i, safe="") + "?vcf_string=1")
    for item in d or []:
        for allele, v in item.items():
            if isinstance(v, dict):
                for vs in v.get("vcf_string", []):
                    m = re.match(r"^(\d+|X|Y)-(\d+)-([ACGTN]+)-([ACGTN]+)$", vs)
                    if m:
                        return i, m.groups()
    return i, None


with ThreadPoolExecutor(6) as ex:
    for i, v in ex.map(one, [i for i in ids if i not in recoded]):
        if v:
            recoded[i] = v
print("recoded via Ensembl", len(recoded), "of", len(ids), flush=True)


def canonical(gene):
    if gene not in canon:
        d = get(f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene}?expand=1")
        tx = None
        if d:
            for t in d.get("Transcript", []):
                if t.get("is_canonical"):
                    tx = t["id"]
        canon[gene] = tx
        time.sleep(0.1)
    return canon[gene]


def resolve(gene, tx, hg):
    hg = re.sub(r"\s+", "", hg)
    if not re.match(r"^[cn]\.", hg):
        return None
    if tx.startswith("NM_") or tx.startswith("NR_"):
        d = get("https://rest.variantvalidator.org/VariantValidator/variantvalidator/GRCh38/"
                + urllib.parse.quote(f"{tx}:{hg}", safe="") + "/mane_select?content-type=application%2Fjson")
        time.sleep(1.2)
        for k, v in (d or {}).items():
            if isinstance(v, dict) and v.get("primary_assembly_loci"):
                g = v["primary_assembly_loci"].get("grch38", {}).get("vcf")
                if g:
                    return g["chr"].replace("chr", ""), g["pos"], g["ref"], g["alt"]
        return None
    enst = canon.get(gene)
    if not enst:
        return None
    if f"{enst}:{hg}" in recoded:
        return recoded[f"{enst}:{hg}"]
    return None
    d = get("https://rest.ensembl.org/variant_recoder/human/" + urllib.parse.quote(f"{enst}:{hg}", safe="") + "?vcf_string=1")
    time.sleep(0.1)
    for item in d or []:
        for allele, v in item.items():
            if isinstance(v, dict):
                for s in v.get("vcf_string", []):
                    m = re.match(r"^(\d+|X|Y)-(\d+)-([ACGTN]+)-([ACGTN]+)$", s)
                    if m:
                        return m.groups()
    return None


fetal = {}
for r in rows:
    k = f"{r['cohort']}|{r['case']}"
    if k in fetal or r["cohort"] == "uog_odyssey":
        continue
    fetal[k] = r
log = csv.writer(open(f"{OUT}/resolve.tsv", "w"), delimiter="\t")
log.writerow(["fetus", "gene", "transcript", "hgvs", "zygosity", "chrom", "pos", "ref", "alt"])
var = {}
for k, r in fetal.items():
    genes = [g.strip() for g in r["genes"].split(";") if g.strip()]
    hgs = [h.strip() for h in r["hgvs_c"].split(";")]
    txs = [t.strip() for t in r["transcript"].split(";")] if r["transcript"] else [""] * len(hgs)
    zys = [z.strip() for z in r["zygosity"].split(";")] if r["zygosity"] else [""] * len(hgs)
    out = []
    for i, h in enumerate(hgs):
        g = genes[i] if i < len(genes) else genes[0]
        tx = txs[i] if i < len(txs) else (txs[0] if txs else "")
        z = zys[i] if i < len(zys) else (zys[0] if zys else "")
        v = resolve(g, tx, h)
        log.writerow([k, g, tx, h, z] + (list(v) if v else ["", "", "", ""]))
        out.append((g, z, v))
    var[k] = out
print("fetuses", len(var), "all variants resolved", sum(all(v for _, _, v in x) for x in var.values()), flush=True)

bgs = {}
for name in ("HG005", "HG002"):
    p = f"{G}/{name}.cds.vcf.gz"
    if not os.path.exists(p):
        subprocess.run(f"bcftools view -R {G}/cds50.bed {G}/{name}.vcf.gz | bcftools norm -d exact -Oz -o {p} && tabix -f -p vcf {p}",
                       shell=True, check=True)
    hdr, body = [], []
    with gzip.open(p, "rt") as f:
        for line in f:
            (hdr if line.startswith("#") else body).append(line)
    bgs[name] = (hdr, body)

order = {c: i for i, c in enumerate([str(i) for i in range(1, 23)] + ["X", "Y", "MT"])}
manifest, batch = {}, []
for k, vs in var.items():
    if not vs or any(v is None for _, _, v in vs):
        continue  # require every reported variant to be resolved
    resolved = vs
    name = "HG005" if k.split("|")[0] in CHINA else "HG002"
    hdr, body = bgs[name]
    pre = "chr" if body[0].startswith("chr") else ""
    inj = {}
    zy_all = [z.lower() for _, z, _ in resolved]
    for g, z, (c, pos, ref, alt) in resolved:
        zl = z.lower()
        gt = "1/1" if zl.startswith("hom") else "1" if zl.startswith("hemi") and c == "X" else "0/1"
        inj[(c, int(pos))] = f"{pre}{c}\t{pos}\t.\t{ref}\t{alt}\t50\tPASS\t.\tGT\t{gt}\n"
    rec = [l for l in body if (l.split("\t", 2)[0].replace("chr", ""), int(l.split("\t", 2)[1])) not in inj] + list(inj.values())
    rec.sort(key=lambda l: (order.get(l.split("\t")[0].replace("chr", ""), 99), int(l.split("\t")[1])))
    fid = re.sub(r"[^A-Za-z0-9_-]", "_", k)
    p = f"{OUT}/{fid}.vcf"
    with open(p, "w") as f:
        f.writelines(hdr); f.writelines(rec)
    subprocess.run(["bgzip", "-f", p], check=True); subprocess.run(["tabix", "-f", "-p", "vcf", p + ".gz"], check=True)
    sample = hdr[-1].rstrip("\n").split("\t")[-1]
    feats = "".join(f"  - type:\n      id: {t}\n" for t in terms[k])
    open(f"{OUT}/{fid}.yml", "w").write(f"---\nid: {sample}\nsubject:\n  id: {sample}\n  sex: UNKNOWN_SEX\n"
                                         f"phenotypicFeatures:\n{feats}metaData:\n  createdBy: v1p_prepare\n  phenopacketSchemaVersion: 1.0\n")
    batch.append(f"--sample {OUT}/{fid}.yml --vcf {OUT}/{fid}.vcf.gz --assembly hg38 --preset exome "
                 f"--output-format TSV_GENE,TSV_VARIANT --output-directory {OUT}/results --output-filename {fid}")
    manifest[fid] = {"key": k, "genes": sorted({g for g, _, _ in resolved}), "background": name}
open(f"{OUT}/batch.txt", "w").write("\n".join(batch) + "\n")
json.dump(manifest, open(f"{OUT}/manifest.json", "w"), indent=1)
print("fetuses simulated", len(manifest), "of", len(var))
