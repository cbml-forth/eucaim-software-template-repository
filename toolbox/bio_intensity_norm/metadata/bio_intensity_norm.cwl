cwlVersion: v1.2
class: FEMTask

id: bio_intensity_norm
label: Biologically motivated normalization techniques
doc: >
  The tool is designed to perform normalization at the image-level. This
  normalization method aims to reduce the variability in the intensity values
  of the Magnetic Resonance (MR) prostate images due to different scanners,
  acquisition protocols and conditions, based on the intensity values of
  specific tissues. This tool implements three biologically-motivated intensity
  normalization techniques: (1) The fat-based normalization method, (2) The
  muscle-based normalization method, and (3) The single tissue (fat or muscle)
  piece-wise normalization method.

requirements:
  - class: DockerRequirement
    dockerPull: harbor.eucaim.cancerimage.eu/processing-tools/n4filter:fem

inputs:
  input_dir:
    type: Directory
    doc: Directory containing the DICOM images in the standard structure (i.e. <patient>/<study>/<series>).
    required: true
    default: null
    hidden: false
    source: user
    inputBinding:
      position: 1

  output_dir:
    type: Directory
    doc: Directory where the output files will be written
    default: null
    required: true
    hidden: false
    source: user
    inputBinding:
      position: 2

  fat_based:
    type: boolean
    doc: If specified, the fat-based normalization algorithm is applied
    default: false
    required: false
    hidden: false
    inputBinding:
      position: 3
      prefix: -f

  muscle_based:
    type: boolean
    doc: If specified, the muscle-based normalization algorithm is applied
    default: false
    required: false
    hidden: false
    inputBinding:
      position: 4
      prefix: -f



outputs:
  normalized_output_dir:
    type: Directory
    doc: Output directory containing normalized images
    outputBinding:
      glob: $(inputs.output_dir)

baseCommand: [] # entrypoint has the `python src/main.py` command so you just need to pass the additional parameters only

expectedExitCode: 0  

metadata:                 
  author: Aikaterini Dovrou, Stelios Sfakianakis
  version: "1.7"
  orchestrator:
    network: overlay
