"""Fu 2022 Table S3 HGVS (RefSeq c.) -> GRCh38 VCF records via Ensembl variant_recoder.
Writes data/fu_variants_grch38.tsv: case, gene, hgvs, chrom, pos, ref, alt, zygosity, origin."""
import os, csv, json, re, sys, time, urllib.request, urllib.parse, urllib.error

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(f"{B}/data/fu_s3_variants.tsv"), delimiter="\t"))
items = []
prev = None
for r in rows:
    if not r["Transcript"].strip() and prev and r["Case ID"] == prev["Case ID"]:
        r["Transcript"] = prev["Transcript"]; r["Gene(OMIM ID)"] = r["Gene(OMIM ID)"] or prev["Gene(OMIM ID)"]
    prev = r
    gene = re.sub(r"\(.*", "", r["Gene(OMIM ID)"]).replace("*", "").strip()
    c = r["Nucleotide change"].replace("*", "").strip()
    tx = r["Transcript"].strip()
    if not (gene and c.startswith("c.") and tx.startswith("NM_")):
        items.append((r, gene, None)); continue
    items.append((r, gene, f"{tx}:{c}"))


def recode(batch):
    out = []
    for h in batch:
        url = "https://rest.ensembl.org/variant_recoder/human/" + urllib.parse.quote(h, safe="") + "?fields=vcf_string"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        for t in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as f:
                    out += json.load(f); break
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    print("unresolvable", h, file=sys.stderr); break
                time.sleep(5 * (t + 1))
            except Exception:
                time.sleep(5 * (t + 1))
        time.sleep(0.07)
    return out


ids = sorted({h for _, _, h in items if h})
out = {}
for i in range(0, len(ids), 100):
    for d in recode(ids[i:i + 100]):
        for allele, v in d.items():
            if not isinstance(v, dict):
                continue
            inp = v.get("input") or d.get("input")
            vs = [s for s in v.get("vcf_string", []) if re.match(r"^(\d+|X|Y)-\d+-", s)]
            if inp and vs:
                out.setdefault(inp, vs[0])
    time.sleep(1)

w = csv.writer(open(f"{B}/data/fu_variants_grch38.tsv", "w"), delimiter="\t")
w.writerow(["case", "gene", "hgvs", "chrom", "pos", "ref", "alt", "zygosity", "origin", "variant_type"])
ok = 0
for r, gene, h in items:
    vs = out.get(h) if h else None
    if vs:
        ch, pos, ref, alt = vs.split("-", 3); ok += 1
    else:
        ch = pos = ref = alt = ""
    w.writerow([r["Case ID"], gene, h or r["Nucleotide change"], ch, pos, ref, alt,
                r["Zygosity"], r["Origin"], r["Variant type"]])
print("rows", len(items), "hgvs", len(ids), "recoded", ok)
