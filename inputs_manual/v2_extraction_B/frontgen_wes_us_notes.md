# frontgen_wes_us (extractor B)
- Source: Table 2 (33 fetuses with P/LP variants). Table 3 (no P/LP) not used.
- Listed 33, included 32, excluded 1: case 32 SDHB (authors call it incidental, it does not explain the phenotype).
- Rows 95; manual mappings 21 rows (19 distinct texts).
## Judgement calls
- Case 15 HBA1/HBA2 --SEA/--SEA: a gene-level deletion (CNV-type allele) but reported as a P monogenic diagnosis (alpha-thalassaemia); included. DOUBT: may count as a "CNV only" exclusion.
- Case 20 SLC12A1: single het P variant in an AR gene, but the authors report it as explanatory; included. DOUBT.
- Case 11 DUOX2 (thyroid dyshormonogenesis for ASD) and case 6 PKD1: included because the authors count them among the 32 explanatory diagnoses.
- "hydrops" (case 20) matched the exact synonym of HP:0000969 Edema by rule; Hydrops fetalis (HP:0001789) would also be justified.
- The cells that break across lines in XML were rejoined ("Thickened nuchal skin Fold", "Hyperechogenic Kidneys"). Typos were kept as printed ("dilation oflateralventricles", "talipesequinovarus", "Flexioncontracture", stray ")").
- Intracranial multiple hyperechoic nodules -> Abnormal brain morphology (location unspecified). Polycystic kidney -> Polycystic kidney dysplasia. Left femur curvature -> Femoral bowing (laterality dropped). Bipedal / left hand cleft deformity -> Split foot / Split hand.
- hgvs_c: only the c. part is kept (p. dropped). The OBSL1 "c.458dupG" was split from the merged p. text. No transcripts or per-case GA are given.
- zygosity for compound het = "Het;Het"; origin as printed.
