# Tabular Data Curation (TDC)

The TDC (Tabular Data Curation) tool takes as input a tabular dataset (e.g. clinical and imaging
metadata) in `.csv`, `.xlsx` or a specified `.json` format and produces five user-friendly reports
(in `.xlsx` format) summarising metadata and feature-level diagnostics, problematic fields, as well
as highly correlated and lexically similar pairs of features. TDC also produces a `.json` file which
holds all of the above information in a structured, machine-readable form.

This is the EUCAIM software-template-compliant packaging of TDC. The original standalone
Flask/web-GUI version of the tool is maintained at [github.com/vpz4/TDC](https://github.com/vpz4/TDC).
For this template, the web front end has been removed and replaced with a command line interface
(`-i`/`-o`) so the tool can run as a containerized, non-interactive task within the EUCAIM Federated
Execution Manager (FEM).

### Structure of this folder

```text
tabular-data-curator/
├── README.md
├── LICENSE
├── NOTICE
├── docs/
│   └── README.md              # short summary, contacts and links
├── task_containers/
│   └── tdc/
│       ├── dockerfile
│       ├── entrypoint.sh
│       └── app/
│           ├── main.py        # CLI entry point + all TDC processing logic
│           └── requirements.txt
├── metadata/
│   └── tdc.cwl                # FEM task descriptor
└── test/
    ├── example_input/
    │   └── test.csv
    └── example_output/
        ├── description.md     # notes on non-deterministic output fields
        └── ...                # reference reports for test.csv
```

### Input & Output

* **Input**: a single tabular dataset in `.csv`, `.xlsx` or `.json` format, passed via `-i`. The
  `-i` argument accepts either a direct file path, or a directory containing exactly one supported
  dataset file (the latter matches how EUCAIM mounts a node's data folder).
* **Output**: written to the directory passed via `-o`:
  * a data quality evaluation report (`*_evaluation_report.xlsx`) summarising metadata and
    feature-level diagnostics,
  * a curated dataset (`*_curated_dataset.xlsx`) - the original dataset with problematic fields
    (e.g. outliers, missing values, inconsistencies) highlighted using colour coding,
  * a clean curated dataset (`*_curated_dataset_clean.xlsx`) - the curated dataset with
    low-quality features (>30% missing values) automatically removed,
  * a similarity report (`*_similarity_report_corr.xlsx`) summarising highly correlated pairs of
    features (if any),
  * a similarity report (`*_similarity_report_lex.xlsx`) summarising lexically similar pairs of
    features (if any),
  * a structured `*_results.json` file combining all of the above information.

### Functionalities

* Outlier detection method (`--outlier-method`, default `1`):
  1. z-score
  2. z-score (mod.) - robust variant using median/MAD, recommended
  3. Interquartile range (IQR)
  4. Grubb's test
  5. Local Outlier Factor (LOF) - currently ignored (sensitive to data type errors)
  6. Isolation Forests
  7. Isolation Forests (mod.)
* Similarity detection method (`--similarity-method`, default `1`):
  1. Spearman rank-order correlation coefficient - recommended
  2. Pearson's correlation coefficient
  3. Kendall's tau
  4. Covariance
  5. None
  * The lexical similarity report (Jaro distance between feature labels) is always produced and
    does not depend on this option.
* Data imputation method (`--imputation-method`, default `1`):
  1. Average/median
  2. Random
  3. Zeros
  4. None

### Guide

Build the image:

```bash
cd task_containers/tdc
docker build -t tabular-data-curator .
```

Run the container against the example dataset:

```bash
docker run --rm \
  -v $(pwd)/../../test/example_input:/app/input_data:ro \
  -v $(pwd)/../../test/example_output:/app/output_data \
  tabular-data-curator
```

Or pass parameters explicitly:

```bash
docker run --rm \
  -v $(pwd)/../../test/example_input:/app/input_data:ro \
  -v $(pwd)/../../test/example_output:/app/output_data \
  tabular-data-curator python3 main.py \
  -i /app/input_data -o /app/output_data \
  --outlier-method 2 --similarity-method 1 --imputation-method 1
```

Running outside Docker (e.g. for development):

```bash
cd task_containers/tdc/app
pip install -r requirements.txt
python3 main.py -i /path/to/dataset.csv -o /path/to/output_dir
```

### Technical information

* CPU: monolithic algorithmic implementation / no GPU required.
* Programming language: Python 3.9.
* Expected RAM usage: up to 16GB depending on dataset size.
* Running mode: case-based (single dataset per invocation).

### Main publication

* Pezoulas, Vasileios C., et al. "Medical data quality assessment: On the development of an
  automated framework for medical data curation." Computers in biology and medicine 107 (2019):
  270-283. https://www.sciencedirect.com/science/article/pii/S0010482519300733

### Related EU projects where the tool has been deployed

* SILICOFCM - In Silico trials for drug tracing the effects of sarcomeric protein mutations
  leading to familial cardiomyopathy (Grant agreement ID: 777204)
* HarmonicSS - HARMONIzation and integrative analysis of regional, national and international
  Cohorts on primary Sjögren's Syndrome (pSS) towards improved stratification, treatment and
  health policy making (Grant agreement ID: 731944)
* EUCAIM - European Cancer Imaging Initiative (Grant agreement ID: 101100633)

### Successful applications of the TDC tool

* Pezoulas, Vasileios C., et al. "Enhancing medical data quality through data curation: A case
  study in primary Sjögren's syndrome." Clin. Exp. Rheumatology 37.3 (2019): 90-96.
  https://pubmed.ncbi.nlm.nih.gov/31287405/
* Pezoulas, Vasileios C., et al. "Distilling knowledge from high quality biobank data towards the
  discovery of risk factors for patients with cardiovascular diseases and depression." 2023 IEEE
  EMBS International Conference on Biomedical and Health Informatics (BHI). IEEE, 2023.
  https://ieeexplore.ieee.org/document/10313449
* Pezoulas, Vasileios C., et al. "A computational pipeline for data augmentation towards the
  improvement of disease classification and risk stratification models: A case study in two
  clinical domains." Computers in Biology and Medicine 134 (2021): 104520.
  https://www.sciencedirect.com/science/article/pii/S0010482521003140
