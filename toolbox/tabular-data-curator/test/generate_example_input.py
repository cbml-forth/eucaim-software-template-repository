#!/usr/bin/env python3
"""Generate the synthetic, non-confidential TDC test case in EUCAIM CDM file-structure format.

Writes test/example_input/clinical_mandatory_view.csv: 30 synthetic patients using the
clinical_mandatory_view columns and CDM codes of the cdm_federated_unbalance_checker example
(toolbox/cdm_federated_unbalance_checker/test/generate_datasets.py), with a few injected
data-quality issues so every TDC check has something to report:

* cancer_condition_age_at_diagnosis: 2 missing values and 1 implausible value (210) -> outlier
* first_treatment_type: 5 missing values (17%)            -> "fair" feature
* patient_ethnicity: 24 missing values (80%)              -> "bad" feature, dropped in the clean dataset
* evidence_procedure_code: 2 codes without their "CLIN" prefix (numeric) -> mixed types, incompatibility

Deterministic (fixed seed, seeded patient IDs). Run from this folder: python3 generate_example_input.py
"""
import csv
import os
import random

rng = random.Random(42)
N = 30

COLUMNS = [
    "cancer_condition_age_at_diagnosis", "patient_birth_sex", "patient_ethnicity", "dataset_id",
    "patient_id", "patient_diagnostic_category", "first_treatment_type", "evidence_procedure_code",
    "cancer_condition_type", "cancer_condition_topography", "cancer_condition_histology_morphology",
    "cancer_condition_code", "cancer_condition_age_unit",
]
SEX = ["COM1001366", "COM1001370"]
ETHNICITY = ["COM1001311", "COM1001046"]
DIAGNOSTIC = ["COM1001086", "COM1001087", "COM1002624", "COM1002625", "COM1002626", "COM1002628"]
TREATMENT = ["CLIN1034187", "CLIN1035100", "CLIN1014763", "CLIN1014764", "CLIN1034262",
             "CLIN1049098", "CLIN1014933", "CLIN1004413", "CLIN1034674", "CLIN1010523"]
PROCEDURE = ["CLIN1000242", "CLIN1000243", "CLIN1000248", "CLIN1001712", "CLIN1001713",
             "CLIN1001714", "CLIN1001715", "CLIN1001716", "CLIN1001717", "CLIN1001718"]
TOPOGRAPHY = ["BP1000021", "BP1000051", "BP1000075", "BP1000142", "BP1000192", "BP1000209",
              "BP1000286", "BP1000290", "BP1000291", "BP1000298", "BP1000299", "BP1000301"]
HISTOLOGY = ["CLIN1000061", "CLIN1000063", "CLIN1000066", "CLIN1000067", "CLIN1000069",
             "CLIN1000073", "CLIN1000081", "CLIN1000082", "CLIN1000113", "CLIN1000132"]
CONDITION = ["CLIN1000045", "CLIN1000053", "CLIN1000054", "CLIN1000057", "CLIN1000058",
             "CLIN1000060", "CLIN1000062", "CLIN1000065", "CLIN1000068", "CLIN1000071"]


def main():
    rows = []
    for i in range(N):
        age = min(90, max(35, int(round(rng.gauss(64, 9)))))
        rows.append({
            "cancer_condition_age_at_diagnosis": age,
            "patient_birth_sex": SEX[i % 2],
            "patient_ethnicity": rng.choice(ETHNICITY),
            "dataset_id": "ds-tdc",
            "patient_id": "%032x" % rng.getrandbits(128),
            "patient_diagnostic_category": rng.choice(DIAGNOSTIC),
            "first_treatment_type": rng.choice(TREATMENT),
            "evidence_procedure_code": rng.choice(PROCEDURE),
            "cancer_condition_type": rng.choice(["COM1000017", "COM1000159"]),
            "cancer_condition_topography": rng.choice(TOPOGRAPHY),
            "cancer_condition_histology_morphology": rng.choice(HISTOLOGY),
            "cancer_condition_code": rng.choice(CONDITION),
            "cancer_condition_age_unit": "COM1000151",
        })

    # Injected data-quality issues (fixed positions so the expected output is stable)
    for i in (4, 17):
        rows[i]["cancer_condition_age_at_diagnosis"] = ""
    rows[11]["cancer_condition_age_at_diagnosis"] = 210
    for i in (2, 9, 15, 22, 27):
        rows[i]["first_treatment_type"] = ""
    for i in range(N):
        if i not in (0, 7, 13, 19, 24, 29):
            rows[i]["patient_ethnicity"] = ""
    for i in (6, 20):
        rows[i]["evidence_procedure_code"] = rows[i]["evidence_procedure_code"].replace("CLIN", "")

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_input")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "clinical_mandatory_view.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {N} synthetic patients to {out_dir}/clinical_mandatory_view.csv")


if __name__ == "__main__":
    main()
