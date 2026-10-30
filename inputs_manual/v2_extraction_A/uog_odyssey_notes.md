# uog_odyssey extraction notes (extractor A)

## Inclusion
Source: supp UOG-68-388-s001.xlsx, Tables S2 (HR-FSA, n=22) and S3 (LR-FSA, n=20); S4 (no FSA, n=59). Children diagnosed postnatally (100KGP genome / DDD exome) with validated P/LP variants; prenatal phenotype taken from prenatal records (Viewpoint ultrasound system).
- Listed: 101 children. Included: 42 (22 HR-FSA + 20 LR-FSA). Excluded: 59 (Table S4, no prenatal structural anomaly recorded).
- Table S1 duplicates S2/S3 cases; 3 S1 cases (ODSY083, ODSY099, ODSY119) have prenatal phenotype "None" (anomalies neonatal only) -> not included.

## Output
- Rows: 109; fetuses: 42; manual mappings: 69 findings (82 rows).

## Judgement calls
- Only the "Prenatal Phenotype" column used; "Neonatal Findings Which Could be Detected in Utero" and paediatric phenotype ignored (postnatal).
- No transcript/HGVS in source. The source "Inheritance" column holds origin (De Novo/Maternal/Biparental) -> written to `origin`; `inheritance` (AD/AR/XL) left empty because not reported.
- ODSY074 (PIK3CA): columns shifted in source (Zygosity "De Novo - Mosaic", Inheritance "Pathogenic"); zygosity kept as printed, origin left empty.
- ODSY095 (UBA5, AR gene): zygosity/inheritance "Unknown" as printed; "normal bladder" not extracted (normal finding).
- ODSY005 "Blocked Tear Ducts" is listed as a prenatal phenotype; kept and mapped to Nasolacrimal duct obstruction (doubt: may not be an imaging finding).
- Non-structural prenatal items kept as reported: "placental insufficiency" (-> Abnormalities of placenta or umbilical cord), "reduced movement" (-> Decreased fetal movement), "Queries over Increased Size" (suspected LGA -> Large for gestational age).
- Comma splitting with manual corrections: "Borderline ventriculomegaly (9-11) 6.3mm increased NT" split into two findings; "Prominent forehead. Thorax lymph oedema" split at the period.
- Two-entity findings given two rows: e.g. "Cystic Hygroma and Pleural Effusion", "hydronephrosis and AVSD", "Large For Gestational Age and Polyhydramnios", "Small bladder with surrounding ascites", "Some IUGR - Likely placental insufficiency"; three rows for "Absent left AV valve with single ventricle and double outlet ventricle".
- "hypercirculation in middle cerebral artery ... lymphangioma" -> Elevated fetal MCA peak systolic velocity (doubt); the lymphangioma interpretation not mapped.
- "Left microcystic lung lesion" -> Abnormal lung morphology (CPAM not stated). "midline pushed to the side" -> Abnormal brain morphology.
- Severity/size modifiers without an HPO term dropped (severe ventriculomegaly -> Ventriculomegaly); borderline/mild -> Mild fetal ventriculomegaly.

## Manual HPO mappings
- "Unspecified Slow Fetal Growth" -> HP:0001511 Intrauterine growth retardation
- "Borderline ventriculomegaly (9-11)" -> HP:0010952 Mild fetal ventriculomegaly
- "6.3mm increased NT" -> HP:0010880 Increased nuchal translucency
- "Femur less than 10th centile" -> HP:0003097 Short femur
- "potentially absent stomach" -> HP:0010963 Absence of stomach bubble on fetal sonography
- "Unexplained IUGR" -> HP:0001511 Intrauterine growth retardation
- "asymmetrical growth" -> HP:0001507 Growth abnormality
- "reduced movement" -> HP:0001558 Decreased fetal movement
- "Situs Invertus - Stomach on incorrect side" -> HP:0003363 Abdominal situs inversus
- "Increased NT" -> HP:0010880 Increased nuchal translucency
- "Abnormal 4 heart chamber with possible VSD" -> HP:4000105 Abnormal four chamber view of the fetal heart; HP:0001629 Ventricular septal defect
- "Complex cardiac double outlet right ventricle" -> HP:0001719 Double outlet right ventricle
- "Cystic Hygroma and Pleural Effusion" -> HP:0000476 Cystic hygroma; HP:0002202 Pleural effusion
- "Abnormal echocardiogram" -> HP:0500015 Abnormal cardiac test
- "Hydrops Fetalis not due to Haemolytic disease" -> HP:0001790 Nonimmune hydrops fetalis
- "Moderate bilateral vetriculomegaly (14-15mm) became aysmmetrical 43mm left side" -> HP:0002119 Ventriculomegaly; HP:0100960 Lateral ventricular asymmetry
- "moderately dilated 3rd ventricle" -> HP:0007082 Dilated third ventricle
- "head circumference above 90th percentile" -> HP:0040194 Increased head circumference
- "midline pushed to the side" -> HP:0012443 Abnormal brain morphology
- "small hepatic cyst" -> HP:0001407 Hepatic cysts
- "few dilated loops of bowel" -> HP:4000140 Fetal bowel dilatation
- "Abnormal cavum septum pellucidum" -> HP:0007375 Abnormal septum pellucidum morphology
- "venticulomegaly (3rd ventricle - 7mm)" -> HP:0002119 Ventriculomegaly
- "third ventricle dilated" -> HP:0007082 Dilated third ventricle
- "severe bilateral ventriculomegaly >15mm" -> HP:0002119 Ventriculomegaly
- "Absent left AV valve with single ventricle and double outlet ventricle" -> HP:0006705 Abnormal atrioventricular valve morphology; HP:0001750 Single ventricle; HP:4000143 Abnormal fetal heart outflow tract
- "mild left ventriculomegaly" -> HP:0010952 Mild fetal ventriculomegaly
- "Congenital diaphragmatic hernia, left side contains stomach" -> HP:0000776 Congenital diaphragmatic hernia
- "right kidney abnormal" -> HP:0012210 Abnormal renal morphology
- "Thorax lymph oedema" -> HP:0001004 Lymphedema
- "severe ventriculomegaly" -> HP:0002119 Ventriculomegaly
- "hypercirculation in middle cerebral artery which would be in keeping with findings of lymphangioma" -> HP:0034191 Elevated fetal middle cerebral artery peak systolic velocity
- "Lemon Shaped head" -> HP:0032269 Lemon sign
- "severe ventriculomegaly >15mm" -> HP:0002119 Ventriculomegaly
- "cerebellum abnormal shape inferiorly" -> HP:0001317 Abnormal cerebellum morphology
- "lemon shaped cranium" -> HP:0032269 Lemon sign
- "stomach not visible" -> HP:0010963 Absence of stomach bubble on fetal sonography
- "Dandy Walker malformation" -> HP:0001305 Dandy-Walker malformation
- "Septal Defect" -> HP:0001671 Abnormal cardiac septum morphology
- "Moderate Ascites (12mm)" -> HP:0001541 Ascites
- "Bright kidneys" -> HP:0004719 Hyperechogenic kidneys
- "Minimal pyelcatasis both sides" -> HP:0011129 Bilateral fetal pyelectasis
- "Small bladder with surrounding ascites" -> HP:0010476 Aplasia/Hypoplasia of the bladder; HP:0001541 Ascites
- "hydronephrosis both sites with blunted calyces" -> HP:0000126 Hydronephrosis
- "some pressure on thorax due to increasing size of abdomen" -> HP:0003270 Abdominal distention
- "Bilateral enlarged kidneys with dilated collecting systems" -> HP:0000105 Enlarged kidney; HP:0004742 Abnormal renal collecting system morphology
- "bilateral larger hydroureter" -> HP:0000072 Hydroureter
- "hydronephrosis and AVSD" -> HP:0000126 Hydronephrosis; HP:0006695 Atrioventricular canal defect
- "Large For Gestational Age and Polyhydramnios" -> HP:0001520 Large for gestational age; HP:0001561 Polyhydramnios
- "Blocked Tear Ducts" -> HP:0000579 Nasolacrimal duct obstruction
- "Left Renal Cyst - spontaneously resolved" -> HP:0000107 Renal cyst
- "Bilateral Talipes" -> HP:0001883 Talipes
- "oliogohydramnios" -> HP:0001562 Oligohydramnios
- "growth restriction" -> HP:0001511 Intrauterine growth retardation
- "placental insufficiency" -> HP:0001194 Abnormalities of placenta or umbilical cord
- "Left microcystic lung lesion (resolved spontaneously at 29+4)" -> HP:0002088 Abnormal lung morphology
- "Low Amniotic Fluid" -> HP:0001562 Oligohydramnios
- "IUGR at end of Pregnancy" -> HP:0001511 Intrauterine growth retardation
- "Left sided large diaphragmatic hernia with polyhydramnios" -> HP:0000776 Congenital diaphragmatic hernia; HP:0001561 Polyhydramnios
- "Queries over Increased Size" -> HP:0001520 Large for gestational age
- "Increased NT >10mm" -> HP:0010880 Increased nuchal translucency
- "Unspecified Fetal Oedema" -> HP:0000969 Edema
- "Cleft lip and Palate (Difficult to diagnose)" -> HP:0410030 Cleft lip; HP:0000175 Cleft palate
- "Abnormal eyes" -> HP:0012372 Abnormal eye morphology
- "nasal bone not visible" -> HP:0025706 Absent fetal nasal bone
- "Borderline Ventriculomegaly" -> HP:0010952 Mild fetal ventriculomegaly
- "Complex Cardiac - Unspecified" -> HP:0001627 Abnormal heart morphology
- "Tetraology of Fallot" -> HP:0001636 Tetralogy of Fallot
- "Some IUGR - Likely placental insufficiency" -> HP:0001511 Intrauterine growth retardation; HP:0001194 Abnormalities of placenta or umbilical cord
