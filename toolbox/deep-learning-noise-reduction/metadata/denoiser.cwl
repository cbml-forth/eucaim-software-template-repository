cwlVersion: v1.2
class: FEMTask

id: deep-learning-noise-reduction
label: Deep Learning Noise Reduction (DLNR)
doc: A Python tool for reducing noise in medical images

requirements:
  - class: DockerRequirement
    dockerPull: harbor.eucaim.cancerimage.eu/processing-tools/deep-learning-noise-reduction:latest

inputs:
  input_dir:
    type: Directory
    doc: Directory with the input NIfTI files
    required: true
    default: /denoiser/input_data
    hidden: false
    source: user
    inputBinding:
      position: 1
      prefix: -i
      separate: true

  output_dir_name:
    type: string
    doc: Directory where the output NIfTI files will be written
    default: /denoiser/output_data
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
    doc: Directory that contains the output files
    outputBinding:
      glob: $(inputs.output_dir_name)

baseCommand: [] # entrypoint has the `python denoiser.py` command so you just need to pass the additional parameters only

expectedExitCode: 0  

metadata:                 
  author: Stelios Sfakianakis, Eleftherios Trivyzakis
  version: "1.0"
  orchestrator:
    network: overlay