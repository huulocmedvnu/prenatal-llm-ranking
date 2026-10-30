"""Retry HGVS that Ensembl could not recode, via VariantValidator (GRCh38). Updates
data/fu_variants_grch38.tsv in place; writes data/fu_variants_unresolved.tsv."""
import os, csv, json, sys, time, urllib.parse, urllib.request

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = f"{B}/data/fu_variants_grch38.tsv"
rows = list(csv.DictReader(open(P), delimiter="\t"))
fixed, bad = 0, []
for r in rows:
    if r["chrom"] or not r["hgvs"].startswith("NM_"):
        if not r["chrom"]:
            bad.append(r)
        continue
    url = ("https://rest.variantvalidator.org/VariantValidator/variantvalidator/GRCh38/"
           + urllib.parse.quote(r["hgvs"], safe="") + "/mane_select?content-type=application%2Fjson")
    try:
        with urllib.request.urlopen(url, timeout=120) as f:
            d = json.load(f)
        vcf = None
        for k, v in d.items():
            if isinstance(v, dict) and v.get("primary_assembly_loci"):
                g = v["primary_assembly_loci"].get("grch38", {}).get("vcf")
                if g:
                    vcf = g; break
        if vcf:
            r["chrom"] = vcf["chr"].replace("chr", ""); r["pos"] = vcf["pos"]; r["ref"] = vcf["ref"]; r["alt"] = vcf["alt"]
            fixed += 1
        else:
            bad.append(r)
    except Exception as e:
        print("fail", r["hgvs"], e, file=sys.stderr); bad.append(r)
    time.sleep(1.2)
w = csv.DictWriter(open(P, "w"), fieldnames=list(rows[0]), delimiter="\t"); w.writeheader(); w.writerows(rows)
w = csv.DictWriter(open(f"{B}/data/fu_variants_unresolved.tsv", "w"), fieldnames=list(rows[0]), delimiter="\t")
w.writeheader(); w.writerows(bad)
print("fixed", fixed, "still unresolved", len(bad), "resolved total", sum(1 for r in rows if r["chrom"]))
