# FeaturesHarmonization

## Description

The tool is designed to perform harmonization at the feature-level. The tool offers two methods: 
1. ComBat method, which shifts the radiomics features to the overall mean and pooled variance of all centers, 
2. M-ComBat method, which shifts the radiomics features to the mean and variance of the chosen reference center with the most samples. 


### Input/output description:

The **input** of the tool is a directory that should contain two CSV files: 

1. The `radiomics.csv` file should contain the radiomic features of each patient. The file should have a column named "PatientID" in which each row has the patient ID and the radiomics names columns in which each row contains the radiomic value per patient ID. 
2. The `metadata.csv` file should contain the corresponding metadata of each patient. This csv file should have a column named "PatientID" in which each row has the patient ID, a column named `Manufacturer` or/and `ManufacturerModelName` in which each row contains the manufacturer’s name or/and the manufacturer’s model name that each patientID was scanned at. 

The **output** is the harmonized radiomic features for all patients, which are saved to the output directory specified by the user with the same format (`harmonized_radiomics.csv` file). Also, harmonization estimates and other information are stored in additional pickle files.

## Usage

The tool is dockerized. 

1.	Download the latest version of the docker image (harmonization_v1.5.tar)
2.	Load the docker image by running the following command (assuming you are in the same directory as the tar file):
>	docker load -i harmonization_v1.5.tar
3.	Run the following command in order to create a container and instantiate the docker image:

```
docker run --rm \
  -v "your_input_path:/data/input" \
  -v "your_output_path/:/data/output"
 harmonization:1.5 /data/input /data/output [-h] [-M] [-c]
```

where *your_input_path* is the folders path that containts the radiomics and the metadata csv files. *your_output_path* is the output dictory path where the harmonized radiomic features and the harmonization parameters files are stored.

The two mandatory arguments:
  * INPUT_DIR: the path that contains the radiomic features and the corresponding metadata of each patient.
  * OUTPUT_DIR: the path where the harmonized radiomic features for all patients will be saved

Other available arguments:

```
  -h, --help            show help / usage information
  -M, --manufacturerModelName
                        If specified, the manufacturer Model variable instead of the (default)manufacturer variable will be used as center-effect.
  -c, --combat          If specified, the ComBat method will be used. If not, the M-ComBat method will be used.
```

## License

This project is licensed under the EUPL-1.2. See the LICENSE file for details.
