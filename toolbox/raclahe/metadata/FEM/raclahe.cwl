cwlVersion: v1.2
class: FEMTask

id: raclahe
label: RACLAHE Image Enhancement
doc: >-
  Region Adaptive Contrast Limited Adaptive Histogram Equalization (RACLAHE)
  for improving CNN-based segmentation of the prostate and prostatic zones in
  T2-Weighted MR images.

requirements:
  - class: DockerRequirement
    dockerPull: harbor.eucaim.cancerimage.eu/processing-tools/raclahe:3.0-fem
  - class: ResourceRequirement
    coresMin: 2
    ramMin: 8192

inputs:
  input_dir:
    type: Directory
    doc: >-
      Directory holding one sub-directory per patient. Each patient
      sub-directory must contain either a DICOM series (*.dcm) or exactly one
      NIfTI file (*.nii / *.nii.gz).
    required: true
    default: /raclahe/input_data
    hidden: false
    source: user
    inputBinding:
      position: 1
      prefix: -i
      separate: true

  output_dir_name:
    type: string
    doc: >-
      Directory where the enhanced studies will be written, under a
      "RACLAHE OUTPUT" sub-directory.
    default: /raclahe/output_data
    required: true
    hidden: false
    source: user
    inputBinding:
      position: 2
      prefix: -o
      separate: true
      valueFrom: $(runtime.outdir)

outputs:
  output_dir:
    type: Directory
    doc: Directory that contains the enhanced studies
    outputBinding:
      glob: $(inputs.output_dir_name)

baseCommand: [] # the entrypoint already runs `python raclahe.py`; only the additional parameters are passed here

expectedExitCode: 0

metadata:
  author: James Zaridis, FORTH
  version: "3.0-fem"
  orchestrator:
    network: overlay
