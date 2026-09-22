cwlVersion: v1.2
class: FEMTask

id: tabular-data-curator
label: Tabular Data Curation (TDC)
doc: A Python tool for data quality evaluation, curation and similarity detection on tabular (clinical/imaging metadata) datasets

requirements:
  - class: DockerRequirement
    dockerPull: harbor.eucaim.cancerimage.eu/processing-tools/tabular-data-curator:latest

inputs:
  input_dir:
    type: Directory
    doc: Directory containing exactly one input dataset file (.csv, .json or .xlsx)
    required: true
    default: /app/input_data
    hidden: false
    source: user
    inputBinding:
      position: 1
      prefix: -i
      separate: true

  output_dir_name:
    type: string
    doc: Directory where the generated reports will be written
    default: /app/output_data
    required: true
    hidden: false
    source: user
    inputBinding:
      position: 2
      prefix: -o
      separate: true
      valueFrom: $(runtime.outdir)

  outlier_method:
    type: int
    doc: "Outlier detection method: 1=z-score, 2=z-score (mod.), 3=IQR, 4=Grubb's test, 5=Local Outlier Factor, 6=Isolation Forests, 7=Isolation Forests (mod.)"
    default: 1
    required: false
    hidden: false
    source: user
    inputBinding:
      prefix: --outlier-method
      separate: true

  similarity_method:
    type: int
    doc: "Similarity detection method: 1=Spearman, 2=Pearson, 3=Kendall's tau, 4=Covariance, 5=None"
    default: 1
    required: false
    hidden: false
    source: user
    inputBinding:
      prefix: --similarity-method
      separate: true

  imputation_method:
    type: int
    doc: "Data imputation method: 1=Average/median, 2=Random, 3=Zeros, 4=None"
    default: 1
    required: false
    hidden: false
    source: user
    inputBinding:
      prefix: --imputation-method
      separate: true

outputs:
  output_dir:
    type: Directory
    doc: Directory that contains the six generated reports (evaluation report, curated dataset, clean curated dataset, two similarity reports and a holistic JSON summary)
    outputBinding:
      glob: $(inputs.output_dir_name)

baseCommand: [] # entrypoint has the `python3 main.py` command so you just need to pass the additional parameters only

expectedExitCode: 0

metadata:
  author: Vasileios C. Pezoulas
  version: "1.0"
  orchestrator:
    network: overlay
