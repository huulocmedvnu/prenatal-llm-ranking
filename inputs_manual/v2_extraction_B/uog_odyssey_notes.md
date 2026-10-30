# uog_odyssey (extractor B)
- Source: supplementary xlsx S2 (HR-FSA, 22) and S3 (LR-FSA, 20); S1 duplicates these. All diagnoses were postnatal (100KGP/DDD WGS/WES), which is allowed.
- Listed 101 children. Included 42 (all with prenatal-record findings). Excluded 59 (S4, no FSA on prenatal records; their neonatal findings were not used).
- Rows 110; manual mappings 83 rows (75 distinct texts).
- No variant HGVS, transcript or GA in the source. Zygosity is as printed (typos kept: "Heterozyous", "Heterzoygous"). "Inheritance" column (De Novo/Maternal/Biparental) -> origin. Inheritance mode is not reported, so that field is empty.
## Judgement calls
- Neonatal-only findings (S1/S3 "Additional Relevant Neonatal Phenotype") were excluded. Postnatal paediatric phenotypes were excluded.
- ODSY074: the sheet shifts columns ("De Novo - Mosaic" in Zygosity, "Pathogenic" in Inheritance). Recorded as zygosity Mosaic, origin De Novo.
- ODSY095 UBA5: zygosity/inheritance "Unknown"; included as the diagnostic gene. "normal bladder" was dropped (normal finding).
- ODSY005 "Blocked Tear Ducts" -> Nasolacrimal duct obstruction. DOUBT whether this is an imaging finding. ODSY033 "Queries over Increased Size" -> LGA (suspected).
- "asymmetrical growth" (with IUGR) -> IUGR, not HP:0100555 (body asymmetry).
- "placental insufficiency" -> Abnormalities of placenta or umbilical cord (no specific term).
- Compound texts were split: "Borderline ventriculomegaly (9-11) 6.3mm increased NT", "Cystic Hygroma and Pleural Effusion", "Abnormal 4 heart chamber with possible VSD", "Absent left AV valve with single ventricle and double outlet ventricle", "Bilateral enlarged kidneys with dilated collecting systems", "hydronephrosis and AVSD", "Large For Gestational Age and Polyhydramnios", "Some IUGR - Likely placental insufficiency", "Prominent forehead. Thorax lymph oedema".
- Two terms per text: ODSY053 ventriculomegaly + asymmetry. ODSY074 MCA hypercirculation -> Abnormal fetal cardiovascular physiology + Lymphangioma (suspected). ODSY095 small bladder with ascites. ODSY058 cleft lip and palate.
- Severe/moderate ventriculomegaly -> Ventriculomegaly (no severity term). Borderline/mild -> Mild fetal ventriculomegaly. Lemon-shaped head/cranium -> Lemon sign (2 rows kept). "double outlet ventricle" (single ventricle) -> Abnormal ventriculoarterial connection. "midline pushed to the side" -> Abnormal brain morphology. "Abnormal echocardiogram" -> Abnormality of the cardiovascular system. "Situs Invertus - Stomach on incorrect side" -> Situs inversus totalis (DOUBT: may be heterotaxy/abdominal situs).
