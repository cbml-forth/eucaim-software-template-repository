
# IQA DCE tool

The purpose of the tool is to provide a complete framework for automatic
detection of image quality for Breast DCE MR images. The assessment is performed
on the first post-contrast dynamic phase in order to assess the most clinically
relevant sequence among a number of identical acquisitions. Two categories are
available for image classification, i.e. high and low quality, depending on the
level of noise, degree of blurring and presence of artifacts.

## Build and Run

### Build and test in docker 

1. `docker build -t iqa_dce_tool:1.1 .`

2. `docker run --rm iqa_dce_tool:1.1 --help`  


###  Run example usind the provided small sample

```
docker run --rm \
 -v "./smallSample:/containerInputFolderCustom:ro"  \
 -v "./hostOutputFolder:/containerOutputFolderCustom" \
 iqa_dce_tool:1.1 \
  -i /containerInputFolderCustom -o /containerOutputFolderCustom -f CustomOutputFilename.csv
```

###  Run with defaults 
e.g. Analyse all first dynamic phase nifti files in `./hostInput` and its subfolders
Stores `IQA_predictions_<timestamp>.csv` in the same folder

```
docker run --rm -v "./hostInput:/home/inputFolder" iqa_dce_tool:1.1
```


###  Run with custom container folders, custom output file name and read only input folder

```
docker run --rm \
 -v "D:\DockerProjects\iqa\hostInputFolder:/containerInputFolderCustom:ro" \
 -v "D:\DockerProjects\iqa\HostInputFolder:/containerOutputFolderCustom" \
iqa_dce_tool:1.1 \
 -i /containerInputFolderCustom -o /containerOutputFolderCustom -f CustomOutputFilename.csv
```

###  Run with python 

1. Install the required libraries: `pip install -r requirements.txt`
2. Run the code: `python IQA_DCE_tool.py --help`


## Citation

If used in a research project please cite the following article:

```bibtex
@Article{jimaging11110417,
 AUTHOR = {Ioannidis, Georgios S. and Nikiforaki, Katerina and Dovrou, Aikaterini and Kilintzis, Vassilis and Kalliatakis, Grigorios and Diaz, Oliver and Lekadir, Karim and Marias, Kostas},
 TITLE = {Explainable Radiomics-Based Model for Automatic Image Quality Assessment in Breast Cancer DCE MRI Data},
 JOURNAL = {Journal of Imaging},
 VOLUME = {11},
 YEAR = {2025},
 NUMBER = {11},
 ARTICLE-NUMBER = {417},
 URL = {https://www.mdpi.com/2313-433X/11/11/417},
 PubMedID = {41295134},
 ISSN = {2313-433X},
 DOI = {10.3390/jimaging11110417}
}
```

## License

The code of this tool is [licensed](./LICENSE) under the terms of the [EUPL
1.2](https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
license.
