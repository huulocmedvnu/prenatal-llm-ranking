# jcla_karyo_wes extraction notes (extractor A)

## Inclusion
Source: fulltext.xml Table 8 (P/LP concordant with phenotype = diagnostic) and Table 9 (P/LP discordant).
- Listed: 18 (8 in Table 8 + 10 in Table 9; X131 has 2 rows in Table 9). Included: 8 (Table 8). Excluded: 10 Table 9 fetuses (single heterozygous variants in AR genes; authors state they do not explain the phenotype).

## Output
- Rows: 21; fetuses: 8; manual mappings: 10 findings (18 rows).

## Judgement calls
- Findings are category-level only: cardiac type (LVOTO, CTD, RVOTO, SV/Complex SV, Septal defects) and extracardiac system categories. Mapped to the matching category terms (RVOTO -> Abnormal fetal heart outflow tract because HPO has no RVOTO term; doubt).
- Extra findings from the text: both NOTCH1 cases (X113, X203) "presented with aortic atresia and hypoplasia of the ascending aorta and aortic arch, ultimately resulting in hypoplastic left-sided heart syndrome" -> added to both (doubt: X203 is typed "SV/Complex SV" in Table 8). X168 "left ventricular non-compaction ... recurrence in the current fetus" -> added.
- X113 also has a mosaic 1q21.2q44 duplication (~8%) of unclear significance; the NOTCH1 variant is treated as causal.
- X116 transcript printed as "2.1:" (truncated) -> kept as printed. Origin only for trio cases. No per-fetus GA.

## Manual HPO mappings
- "LVOTO" -> HP:0032092 Left ventricular outflow tract obstruction
- "hypoplasia of the ascending aorta and aortic arch" -> HP:0031935 Ascending aorta hypoplasia; HP:0012304 Hypoplastic aortic arch
- "hypoplastic left-sided heart syndrome" -> HP:0004383 Hypoplastic left ventricle
- "left ventricular non-compaction" -> HP:0030682 Left ventricular noncompaction
- "CTD" -> HP:0001710 Conotruncal defect
- "SV/Complex SV" -> HP:0001750 Single ventricle
- "Nervous system anomalies" -> HP:0012639 Abnormal nervous system morphology
- "Skeletal system anomalies" -> HP:0000924 Abnormality of the skeletal system
- "Urinary system anomalies" -> HP:0000079 Abnormality of the urinary system
- "RVOTO" -> HP:4000143 Abnormal fetal heart outflow tract
