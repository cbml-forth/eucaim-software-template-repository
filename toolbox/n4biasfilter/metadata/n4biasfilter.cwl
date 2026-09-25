cwlVersion: v1.2
class: FEMTask

id: n4biasfilter
label: N4 bias filter
doc: A Python tool that performs image pre-processing to reduce the bias field effect, improving the quality of the images

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

  run_n4_filter:
    type: boolean
    doc: Run the N4 filter code
    default: true
    required: true
    hidden: true
    inputBinding:
      position: 3
      prefix: -N

  iterations:
    type: int
    doc: Number of iterations
    default: 50
    required: false
    hidden: false
    source: user
    inputBinding:
      position: 4
      prefix: -I

  threshold:
    type: float
    doc:  Convergence threshold
    default: 0.001
    required: false
    hidden: false
    source: user
    inputBinding:
      position: 5
      prefix: -t

  shrink_factor:
    type: int
    doc:  Shrink factor
    default: 2
    required: false
    hidden: false
    source: user
    inputBinding:
      position: 6
      prefix: -s

  fitting_level:
    type: int
    doc:  Fitting level
    default: 5
    required: false
    hidden: false
    source: user
    inputBinding:
      position: 7
      prefix: -f

outputs:
  n4_filtered_dir:
    type: Directory
    doc: Output directory containing N4 filtered image in a similar structure as the input
    outputBinding:
      glob: $(inputs.output_dir)/N4_filtered

baseCommand: [] # entrypoint has the `python src/main.py` command so you just need to pass the additional parameters only

expectedExitCode: 0  

metadata:                 
  author: Aikaterini Dovrou, Stelios Sfakianakis
  version: "1.8"
  orchestrator:
    network: overlay
