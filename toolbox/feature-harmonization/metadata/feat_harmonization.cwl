cwlVersion: v1.2
class: FEMTask

id: feat-harmonization
label: Radiomics Feature Harmonization
doc: A Python tool that perform harmonization at the imaging feature-level, using either ComBat or M-ComBat. 

requirements:
  - class: DockerRequirement
    dockerPull: harbor.eucaim.cancerimage.eu/processing-tools/feat_harmonization:1.5

inputs:
  input_dir:
    type: Directory
    doc: Directory containing the radiomics.csv and the metadata.csv files.
    required: true
    default: null
    hidden: false
    source: user
    inputBinding:
      position: 1

  output_dir:
    type: Directory
    doc: Directory where the output  files will be written
    default: null
    required: true
    hidden: false
    source: user
    inputBinding:
      position: 2

  manufacturer_model_as_center_effect:
    type: boolean
    doc: If specified, the manufacturer *model* variable will be used as center-effect. Otherwise we use the *manufacturer* variable
    default: false
    required: false
    hidden: false
    source: user
    inputBinding:
      position: 3
      prefix: -M

  use_combat:
    type: boolean
    doc: If specified, the ComBat method will be used. If not, the M-ComBat method will be used.
    default: false
    required: true
    hidden: false
    source: user
    inputBinding:
      position: 4
      prefix: -c

outputs:
  harmonized_radiomics:
    type: File
    doc: CSV file containing the harmonized radiomics feature values
    outputBinding:
      glob: $(inputs.output_dir_name)/harmonized_radiomics.csv

  harmonization_estimates:
    type: File
    doc: Python "pickle" file containing the estimates from the ComBat process
    outputBinding:
      glob: $(inputs.output_dir_name)/harmonization_estimates.pkl

  harmonization_info:
    type: File
    doc: Python "pickle" file containing the (debug) information from the ComBat process
    outputBinding:
      glob: $(inputs.output_dir_name)/harmonization_info.pkl

baseCommand: [] # entrypoint has the `python /home/ds/featuresharmonization/harmonization.py` command so you just need to pass the additional parameters only

expectedExitCode: 0  

metadata:                 
  author: Elisavet Stamoulou, Aikaterini Dovrou
  version: "1.5"
  orchestrator:
    network: overlay