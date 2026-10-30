# ajogmfm_nihf_gs extraction notes (extractor A)

## Inclusion
Source: fulltext.xml Tables 3 and 4 (new GS diagnoses / reportable variants after GS); supp docx Tables S1-S3. Fetuses diagnosed by the earlier ES are not listed per fetus in this paper.
- Listed: 7 (cases 1-7). Included: 1 (case 1). Excluded: 6.
  - Case 2 (LARGE1, AR): both variants are deletions called CNVs by the authors (140 kb and 135 bp) -> excluded under the CNV rule (judgement; intragenic monogenic, adjudicate).
  - Case 3 (SMC1A/HUWE1 mosaic dup): CNV, incidental -> excluded.
  - Case 4 (COL3A1 LP): secondary finding, not causal -> excluded.
  - Cases 5 (RYR1), 6 (PRPF8), 7 (FBXO11): VUS only -> excluded.

## Output
- Rows: 10; fetuses: 1; manual mappings: 4 findings (4 rows).

## Judgement calls
- Case 1 (Hb H disease): 31 kb deletion of HBA2/HBA1/HBM/HBQ1/HBZ (paternal) in trans with HBA2 NM_000517.6:c.179G>A (maternal). Included because an SNV is part of the causal genotype. genes recorded as HBA2;HBA1 (causal alpha-globin genes); hgvs_c lists the genomic deletion first, transcript field empty for it.
- Zygosity not printed (compound genotype). Inheritance AR as printed. GA not given per fetus.
- "skin edema" -> Fetal skin edema; "elevated MCA Doppler" -> Elevated fetal MCA PSV; "hyperplastic myocardium" -> Ventricular hypertrophy (doubt).

## Manual HPO mappings
- "skin edema" -> HP:0025672 Fetal skin edema
- "elevated MCA Doppler" -> HP:0034191 Elevated fetal middle cerebral artery peak systolic velocity
- "enlarged right atrium" -> HP:0030718 Right atrial enlargement
- "hyperplastic myocardium" -> HP:0001714 Ventricular hypertrophy
