cwlVersion: v1.2
class: FEMTask

id: iqa_dce
label: IQA DCE tool
doc: >
  The purpose of the tool is to provide a complete framework for automatic
  detection of image quality for Breast DCE MR images. The assessment is performed
  on the first post-contrast dynamic phase in order to assess the most clinically
  relevant sequence among a number of identical acquisitions. Two categories are
  available for image classification, i.e. high and low quality, depending on the
  level of noise, degree of blurring and presence of artifacts.

requirements:
  - class: DockerRequirement
    dockerPull: harbor.eucaim.cancerimage.eu/ingestion-tools/iqa_dce_tool:1.1-fem

inputs:
  input_dir:
    type: Directory
    doc: Directory with the input NIfTI files
    required: true
    default: null
    hidden: false
    source: user
    inputBinding:
      position: 1
      prefix: -i

  output_dir:
    type: Directory
    doc: Directory where the output file will be written
    default: null
    required: true
    hidden: false
    source: user
    inputBinding:
      position: 2
      prefix: -o

  output_file_name:
    type: string
    doc: The name of the output CSV file
    required: true
    default: IQA_predictions.csv
    hidden: true
    inputBinding:
      position: 3
      prefix: -f

outputs:
  iqa_predictions:
    type: File
    doc: The CSV output file with the binary classification per input NIfTI file
    outputBinding:
      glob: $(inputs.output_dir)/$(inputs.output_file_name)

baseCommand: [] # entrypoint has the `python src/main.py` command so you just need to pass the additional parameters only

expectedExitCode: 0  

metadata:                 
  author: Georgios Ioannidis, Vassilis Kilintzis
  version: "1.1"
  orchestrator:
    network: overlay
