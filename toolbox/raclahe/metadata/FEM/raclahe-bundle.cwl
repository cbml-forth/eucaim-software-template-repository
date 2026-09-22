cwlVersion: v1.2
class: FEMBundle

id: raclahe-bundle
label: RACLAHE Image Enhancement Bundle
doc: >-
  Standalone execution unit applying RACLAHE enhancement to a directory of
  prostate T2-Weighted MR studies.

mode: standalone

tasks:
  - task_id: raclahe
    role: worker
    multiplicity:
      type: single
      doc: A single RACLAHE task processes the whole input directory.

shared_inputs:
  - id: input_dir
    type: Directory
    doc: Directory holding one sub-directory per patient.
    required: true
    default: null
    hidden: false
    constraints: {}
    targets:
      - task_id: raclahe
        task_input_name: input_dir

shared_outputs:
  - id: enhanced_studies
    type: Directory
    doc: Directory containing the RACLAHE-enhanced studies.
    source:
      task_id: raclahe
      task_output_name: output_dir

dependencies: []

metadata:
  author: James Zaridis, FORTH
  version: "3.0-fem"
  orchestrator:
    additional_metadata: {}
