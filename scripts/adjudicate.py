"""Adjudicate the two independent extractions of the post-cutoff cohorts (PLAN_v2).
Base = extraction A; per-finding choices of extraction B listed below; inclusion decisions
listed below; hydrops cohort from B only (A could not access the source).
Writes inputs_manual/v2_cases.csv and inputs_manual/v2_adjudication.csv."""
import glob, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "inputs_manual")
load = lambda d: pd.concat([pd.read_csv(f, dtype=str).fillna("") for f in glob.glob(f"{M}/{d}/*.csv")], ignore_index=True)
A, B = load("v2_extraction_A"), load("v2_extraction_B")
for X in (A, B):
    X["case"] = X.case.str.strip(); X["key"] = X.cohort + "|" + X.case

# fetus inclusion
EXCLUDE = {
    "frontgen_wes_us|15": "homozygous HBA1/HBA2 --SEA deletion: CNV-type allele, CNV rule (as A)",
    "ajogmfm_nihf_gs|2": "biallelic LARGE1 deletions labelled CNV by authors: CNV rule (as A)",
    "frontgen_wes_us|32": "SDHB called incidental by the authors, does not explain phenotype (as B)",
}
# per (fetus, finding text): take extraction B's term(s); reason
TAKE_B = {
    ("frontgen_ep300|3", "FL: M - 2.1SD"): "fetal-specific femur length term",
    ("frontgen_ep300|3", "HL: M - 3.1SD"): "fetal-specific humerus length term",
    ("frontgen_ep300|3", "Bilateral thick plantar surfaces"): "more specific (plantar skin)",
    ("uog_odyssey|ODSY007", "Femur less than 10th centile"): "fetal-specific femur length term",
    ("uog_odyssey|ODSY018", "Left microcystic lung lesion (resolved spontaneously at 29+4)"): "more specific (pulmonary cyst)",
    ("uog_odyssey|ODSY045", "Abnormal echocardiogram"): "phenotype term rather than test term",
    ("uog_odyssey|ODSY061", "venticulomegaly (3rd ventricle - 7mm)"): "third ventricle named in source",
    ("uog_odyssey|ODSY071", "Absent left AV valve"): "B split the compound finding into specific terms",
    ("uog_odyssey|ODSY074", "hypercirculation in middle cerebral artery which would be in keeping with findings of lymphangioma"): "keep A's MCA term and add B's lymphangioma (see ADD)",
}
for c in ["2", "3", "4", "5"]:
    TAKE_B[(f"pd_rnu4atac|{c}", "Microencephaly")] = "microencephaly = small brain, not small head"
for c in ["2", "5"]:
    TAKE_B[(f"pd_rnu4atac|{c}", "Dilated cisterna magna")] = "fetal-specific cisterna magna term"
# terms to add
ADD = {"uog_odyssey|ODSY074": [("hypercirculation in middle cerebral artery which would be in keeping with findings of lymphangioma",
                                "HP:0100764", "Lymphangioma")]}
# single-term corrections
FIX = {("frontgen_wes_us|20", "HP:0000969"): ("HP:0001789", "Hydrops fetalis", "fetal hydrops, not generalised oedema")}

log, rows = [], []
shared = sorted(set(A.key) & set(B.key))
for k in shared:
    if k in EXCLUDE:
        continue
    a, b = A[A.key == k], B[B.key == k]
    for r in a.itertuples(index=False):
        d = r._asdict()
        if (k, d["finding"]) in TAKE_B and k != "uog_odyssey|ODSY074":
            continue  # replaced below by B's rows for this finding
        if k == "uog_odyssey|ODSY071" and d["finding"].startswith("Absent left AV valve"):
            continue  # A's compound finding replaced by B's split terms
        if (k, d["hpo_id"]) in FIX:
            nid, nn, why = FIX[(k, d["hpo_id"])]
            log.append(dict(fetus=k, finding=d["finding"], decision=f"{d['hpo_name']} -> {nn}", reason=why))
            d["hpo_id"], d["hpo_name"], d["map_rule"] = nid, nn, "adjudicated"
        rows.append(d)
    for (kk, f), why in TAKE_B.items():
        if kk != k or k == "uog_odyssey|ODSY074":
            continue
        bb = b[b.finding.str.startswith(f.split(" with ")[0])] if k == "uog_odyssey|ODSY071" else b[b.finding == f]
        if k == "uog_odyssey|ODSY071":
            bb = b[b.finding.isin(["Absent left AV valve", "single ventricle", "double outlet ventricle"])]
        for r in bb.itertuples(index=False):
            d = r._asdict(); d["map_rule"] = "adjudicated (B)"; rows.append(d)
        log.append(dict(fetus=k, finding=f, decision="extraction B term(s)", reason=why))
    for f, hid, hn in ADD.get(k, []):
        base = a.iloc[0]._asdict() if hasattr(a.iloc[0], "_asdict") else a.iloc[0].to_dict()
        base.update(finding=f, hpo_id=hid, hpo_name=hn, map_rule="adjudicated (B)")
        rows.append(base); log.append(dict(fetus=k, finding=f, decision=f"add {hn}", reason=TAKE_B[(k, f)]))
for k, why in EXCLUDE.items():
    log.append(dict(fetus=k, finding="", decision="excluded", reason=why))
for k in sorted(set(A.key) - set(B.key)):
    if k not in EXCLUDE:
        log.append(dict(fetus=k, finding="", decision="CHECK only in A", reason=""))
hyd = B[B.cohort == "hydrops"]
rows += [r._asdict() for r in hyd.itertuples(index=False)]
log.append(dict(fetus="hydrops (all)", finding="", decision=f"included from B only ({hyd.key.nunique()} fetuses)",
                reason="A could not access the full text; single extraction, checked against source_note.md"))
V = pd.DataFrame(rows).drop(columns=["key"]).drop_duplicates()
V.to_csv(f"{M}/v2_cases.csv", index=False)
pd.DataFrame(log).to_csv(f"{M}/v2_adjudication.csv", index=False)
print("fetuses", V.groupby(["cohort", "case"]).ngroups, "rows", len(V))
print(V.groupby("cohort").case.nunique().to_string())
