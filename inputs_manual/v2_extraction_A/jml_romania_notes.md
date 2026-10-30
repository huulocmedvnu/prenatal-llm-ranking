# jml_romania extraction notes (extractor A)

## Inclusion
Source: fulltext.xml Table 1 (10 pregnancies with prenatal WES).
- Listed: 10. Included: 5 (cases 2, 3, 4, 5, 6). Excluded: 5.
  - Case 1: primary result negative, only secondary finding (MYBPC3) -> excluded.
  - Cases 7, 8, 9, 10: WES negative -> excluded.

## Output
- Rows: 13; fetuses: 5; manual mappings: 6 findings (6 rows).

## Judgement calls
- Case 6 (NBAS, AR): P complex allele c.[539_540delinsTG;619C>T] in trans with a "hot VUS" c.6573-1047A>G; authors count it as a positive diagnosis -> included (not VUS-only). Transcript NM_15909.4 is printed only for the VUS (as printed, likely a typo for NM_015909.4).
- Case 5: "suspicion of Meckel–Gruber syndrome" not extracted (diagnostic suspicion, not a finding).
- Case 2: incidental HFE homozygous variant ignored; case 4 ADCY6 and case 6 PROKR2 incidental findings ignored.
- GA = gestational age column of Table 1. Origin not reported (singleton WES).

## Manual HPO mappings
- "Cardiac complex malformation: apex is formed by right ventricle" -> HP:0001627 Abnormal heart morphology
- "hypoplastic left heart" -> HP:0004383 Hypoplastic left ventricle
- "fetal posterior fossa malformation: communication between the fourth ventricle and the cisterna magna" -> HP:0000932 Abnormal posterior cranial fossa morphology
- "Asymmetric shortening of the long bones <1st percentile" -> HP:0003026 Short long bone
- "Fetal skeletal dysplasia involving both upper and lower limbs" -> HP:0002652 Skeletal dysplasia
- "Absent nasal bone" -> HP:0025706 Absent fetal nasal bone
