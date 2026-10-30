# frontgen_wes_us extraction notes (extractor A)

## Inclusion
Source: fulltext.xml Table 2 (33 fetuses with P/LP variants). Table 3 (7 fetuses, no P/LP variant) not eligible.
- Listed: 33 (Table 2). Included: 32. Excluded: 1.
  - Case 15 (HBA1/HBA2 --SEA/--SEA): homozygous Southeast Asian alpha-globin deletion, a CNV-only genotype -> excluded under the CNV rule (judgement; it is a monogenic disease, adjudicate).

## Output
- Rows: 91; fetuses: 32; manual mappings: 16 findings (16 rows).

## Judgement calls
- Case 20 (SLC12A1, AR) has a single heterozygous P variant; authors list it as P/LP in Table 2 -> included as reported (genotype incomplete for AR, flag).
- Case 11 (DUOX2, thyroid dyshormonogenesis) and case 32 (SDHB) have weak phenotype fit; included because listed as P/LP by authors.
- Case 13 AKT1 mosaic: zygosity "Mosaic (51/147)", inheritance "-" as printed.
- Case 6 PKD1 and case 23 ZIC3 outcome "Normal phenotype"; prenatal findings still reported -> included.
- Variant cells: protein notation dropped, only c. kept; multi-line cells joined by ";". Case 14 "c.1304_1305 / delTG" rejoined as c.1304_1305delTG. No transcripts given; no GA per fetus (cohort range 11-36 wk).
- Cell line breaks inside phenotype ("Hyperechogenic / Kidneys", "Thickened nuchal skin / Fold") joined with a space; trailing unmatched ")" removed (cases 18, 19). Typos kept as printed (e.g. "dilation oflateralventricles", "talipesequinovarus").
- "hydrops" (case 20) matched the EXACT synonym of HP:0000969 Edema (not Hydrops fetalis); kept per rule, flag.
- "Intracranial multiple hyperechoic nodules" (TSC2) -> Abnormal brain morphology (location not stated, so not Subependymal nodules).

## Manual HPO mappings
- "Intracranial multiple hyperechoic nodules" -> HP:0012443 Abnormal brain morphology
- "cortical tubercle" -> HP:0009717 Cortical tubers
- "dilation oflateralventricles" -> HP:0006956 Lateral ventricle dilatation
- "talipesequinovarus" -> HP:0001762 Talipes equinovarus
- "orofacialcleft" -> HP:0000202 Orofacial cleft
- "Flexioncontracture" -> HP:0001371 Flexion contracture
- "Polycystic kidney" -> HP:0000113 Polycystic kidney dysplasia
- "enlarged kidneys" -> HP:0000105 Enlarged kidney
- "Short long bones" -> HP:0003026 Short long bone
- "abnormality of calvarial morphology" -> HP:0002683 Abnormal calvaria morphology
- "Left femur curvature" -> HP:0002980 Femoral bowing
- "Right ventricular double outlet" -> HP:0001719 Double outlet right ventricle
- "absence of pulmonary valve" -> HP:0005134 Absence of the pulmonary valve
- "absence of left limb" -> HP:0009827 Amelia
- "Bipedal cleft deformity" -> HP:0001839 Split foot
- "left hand cleft deformity" -> HP:0001171 Split hand
