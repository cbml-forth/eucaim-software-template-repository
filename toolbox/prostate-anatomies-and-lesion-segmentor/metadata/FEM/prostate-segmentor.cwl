cwlVersion: v1.2
class: FEMTask

id: prostate-anatomies-and-lesion-segmentor
label: Prostate Anatomies and Lesion Segmentor
doc: >-
  Cascaded nnU-Net v2 model that segments the whole gland (WG), peripheral zone
  (PZ) and transition zone (TZ) of the prostate from T2-weighted MRI, optionally
  followed by ProLesA-Net for lesion segmentation when matching ADC and DWI
  sequences are provided. Accepts a DICOM series tree in EUCAIM CDM layout or
  NIfTI volumes laid out per patient.

requirements:
  - class: DockerRequirement
    dockerPull: harbor.eucaim.cancerimage.eu/processing-tools/prostate-anatomies-and-lesion-segmentor:2.1.0-fem
  - class: ResourceRequirement
    coresMin: 4
    ramMin: 16384
  - class: CUDARequirement
    cudaVersionMin: "11.7"
    cudaComputeCapability: "6.0"
    cudaDeviceCountMin: 1

inputs:
  input_dir:
    type: Directory
    doc: >-
      Read-only input directory. Either a DICOM tree
      (<patient>/<study>/<series>/*.dcm) or NIfTI volumes per patient
      (<patient>/t2_series.nii.gz plus optional adc_series.nii.gz and
      dwi_series.nii.gz).
    required: true
    default: /app/input_data
    hidden: false
    source: user
    inputBinding:
      position: 1
      prefix: --input
      separate: true

  output_dir_name:
    type: string
    doc: >-
      Writable output directory. Receives one sub-directory per case plus a
      results.json index.
    default: /app/output_data
    required: true
    hidden: false
    source: user
    inputBinding:
      position: 2
      prefix: --output
      separate: true
      valueFrom: $(runtime.outdir)

  input_format:
    type: string
    doc: "Input layout: auto, dicom or nifti."
    default: auto
    required: false
    hidden: false
    source: user
    constraints:
      enum: [auto, dicom, nifti]
    inputBinding:
      position: 3
      prefix: --input-format
      separate: true

  device:
    type: string
    doc: "Inference device: auto, cuda or cpu."
    default: auto
    required: false
    hidden: false
    source: user
    constraints:
      enum: [auto, cuda, cpu]
    inputBinding:
      position: 4
      prefix: --device
      separate: true

  lesion_threshold:
    type: float
    doc: Probability threshold used to binarise the lesion mask.
    default: 0.1
    required: false
    hidden: false
    source: user
    constraints:
      min: 0.0
      max: 1.0
    inputBinding:
      position: 5
      prefix: --lesion-threshold
      separate: true

  save_probs:
    type: boolean
    doc: Also emit probability maps for wg, pz, tz and lesion.
    default: false
    required: false
    hidden: false
    source: user
    inputBinding:
      position: 6
      prefix: --save-probs

outputs:
  output_dir:
    type: Directory
    doc: >-
      Directory with one sub-directory per case (binary masks, optional
      probability maps and DICOM-SEG) plus the results.json index.
    outputBinding:
      glob: $(inputs.output_dir_name)

baseCommand: [] # the entrypoint already runs `python /app/__main__.py`; only the additional parameters are passed here

expectedExitCode: 0

metadata:
  author: Dimitrios Zaridis, FORTH
  version: "2.1.0-fem"
  orchestrator:
    network: overlay
