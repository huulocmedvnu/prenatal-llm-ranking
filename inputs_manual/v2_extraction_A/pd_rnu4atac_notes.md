# pd_rnu4atac extraction notes (extractor A)

## Inclusion
Source: fulltext.xml Table 1 (earliest US anomalies) and Table 2 (US findings at 20+ weeks); supp Table S1 (biometry only).
- Listed: 5. Included: 4 (cases 2-5). Excluded: 1.
  - Case 1: RNU4ATAC genotype established by segregation (targeted) testing of CVS 3 years after TOP, not by exome/genome sequencing -> excluded (judgement; adjudicate).

## Output
- Rows: 36; fetuses: 4; manual mappings: 11 findings (21 rows).

## Judgement calls
- Findings: Table 1 earliest anomalies (GA as printed) plus every "+" or specified entry of Table 2 (GA "20+ weeks"). ACC appears in both tables for case 2; one row kept (Table 1).
- "Microencephaly" and "Microcephaly" are separate rows in the source; both map to Microcephaly (HPO has no micrencephaly term) -> duplicate HPO per fetus, flag.
- "echogenic focus" (case 5) mapped to Echogenic intracardiac focus (organ not stated; doubt).
- Non-coding gene: transcript NR_023343.3, n. notation kept. Zygosity derived from genotype notation (n.[x];[x] = homozygous).

## Manual HPO mappings
- "ACC" -> HP:0001274 Agenesis of corpus callosum
- "Microencephaly" -> HP:0000252 Microcephaly
- "Intracranial cyst" -> HP:0010576 Intracranial cystic lesion
- "Cerebellar vermis agenesis/hypoplasia" -> HP:0006817 Aplasia/Hypoplasia of the cerebellar vermis
- "Dilated cisterna magna" -> HP:0002280 Enlarged cisterna magna
- "Agenesis of corpus callosum (ACC)" -> HP:0001274 Agenesis of corpus callosum
- "Club foot (left)" -> HP:0001762 Talipes equinovarus
- "right hand fixated with ulnar deviation" -> HP:0009487 Ulnar deviation of the hand
- "Hyperechogenic bowl" -> HP:0010943 Echogenic fetal bowel
- "echogenic focus" -> HP:0010942 Echogenic intracardiac focus
- "Mild dilated renal pelvis (4.1 mm)" -> HP:0010946 Dilatation of the renal pelvis
