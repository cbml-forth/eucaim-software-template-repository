cwlVersion: v1.2
class: FEMBundle

id: prostate-anatomies-and-lesion-segmentor-bundle
label: Prostate Anatomies and Lesion Segmentor Bundle
doc: >-
  Standalone execution unit running prostate whole-gland, zonal and lesion
  segmentation over a directory of prostate MRI studies.

mode: standalone

tasks:
  - task_id: prostate-anatomies-and-lesion-segmentor
    role: worker
    multiplicity:
      type: single
      doc: A single task processes the whole input directory.

shared_inputs:
  - id: input_dir
    type: Directory
    doc: Directory of prostate MRI studies (DICOM tree or per-patient NIfTI).
    required: true
    default: null
    hidden: false
    constraints: {}
    targets:
      - task_id: prostate-anatomies-and-lesion-segmentor
        task_input_name: input_dir

shared_outputs:
  - id: segmentations
    type: Directory
    doc: Per-case segmentation masks and the results.json index.
    source:
      task_id: prostate-anatomies-and-lesion-segmentor
      task_output_name: output_dir

dependencies: []

metadata:
  author: Dimitrios Zaridis, FORTH
  version: "2.1.0-fem"
  orchestrator:
    additional_metadata: {}
