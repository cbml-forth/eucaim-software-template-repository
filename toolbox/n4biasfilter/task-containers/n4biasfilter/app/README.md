# custom_n4bias_filter

## Description

The N4 bias filter tool identifies optimal configurations of the N4ITK filter in prostate images and performs the N4 bias field correction. 
Two main options are offered to the user:
1. Apply N4 filter to image/images (either with the default parameters values or with parameters values defined by the user) 
2. Find the optimal configuration of the N4 filter for specific image/images by measuring the Full Width at Half Maximum (FWHM) of the periprostatic fat dstribution. 

### Description of input and output of the available options

### Option 1. Apply N4 filter to images  

**Input**

The **required** input is the *images*, which should be in **DICOM** format. 

At least two volumes are attached to the docker container in order to run the module.
The one volume of the docker container should be a path that contains the folders with the raw images. \
The second volume of the docker container is an output path, which is the path that the N4 filtered images will be stored in the same format. 

**Output**

The output is the N4 filtered images, which are stored in the specified output path.


## Option 2 Apply the whole pipeline to identify the optimal configuration of the N4 filter 

The volumes that are attached to the docker container are the same with those described in Option 1.

### a) To 1 image

**Input**

The **required** input is the *images*, which should be in **DICOM** format.  

**Output**

*optimal_configuration*: string with the optimal configuration of the N4 filter for the specific image in a .txt file

### b) To a batch of images 

**Input**

The **required** input is the *images*, which should be in **DICOM** format. 

**Output**

*optimal_configurations*: an excel file with the optimal configurations of N4 filter identified in a batch of patients.

The optimal configuration, the number of patients that resulted in this configuration and the percentage of patients resulted in this configuration are presented in the first, second and third column, respectively, of the dataframe. 

## Usage
### How to run the code

1. To build the docker image, run the following command:
> docker build -t image_batch_n4filter:1.8 .

2. Save the docker image in a .tar file
> docker save -o image_batch_n4filter_v1.8.tar image_batch_n4filter:1.8

3.	Download the latest version of the docker image (image_batch_n4filter_v1.8.tar)

4.	Load the docker image by running the following command (assuming you are in the same directory as the tar file):
>	docker load -i image_batch_n4filter_v1.8.tar

5. Then, run the following command in order to create a container and instantiate the docker image:
> docker run -it \
  -v "your_input_path:/home/ds/datasets"\
  -v "your_output_path:/home/ds/persistent-home"  \
  image_batch_n4filter:1.8 \
  <INPUT_DIR> <OUTPUT_DIR> [-h] [-N] [-t T] [-s S] [-f F] [-I I] [-m] [-c] [-P]

where *your_input_path* is the path that contains the folders with the raw image of each patient \
      *your_output_path* is the path where the N4 filtered image of each patient will be saved \

The two mandatory arguments: \
  INPUT_DIR: the path that contains the folders with the raw image of each patient \
  OUTPUT_DIR: the path where the N4 filtered image of each patient will be saved

Other available arguments: \
  -h, --help: show this help message and exit \
  -N, --n4filter: Performs N4 bias field correction method \
  -t T, --threshold T: Convergence threshold \
  -s S, --shrinkFactor S: Shrink factor \
  -f F, --fittingLevel F: Fitting level \
  -I I, --Iterations I: Number of iterations \
  -m, --masks: If specified, the N4 algorithm uses masks \
  -c, --custom-masks: Path with whole gland masks. If specified, custom masks are used. If not specified, 
		      the masks will be extracted automatically by the algorithm \
  -P, --pipeline: Apply the whole pipeline to identify the optimal N4 configuration

The two main options are: 
1) Apply N4 filter to image/images, by specifying -N
2) Find the optimal N4 configuration, by specifying -P

## License
This project is licensed under the EUPL-1.2. See the LICENSE file for details.

## Citation

If you use this repository or any of its scripts in your research or software, please cite the following publication:

**Dovrou, A., Nikiforaki, K., Zaridis, D., Manikis, G. C., Mylona, E., Tachos, N., Tsiknakis, M., Fotiadis, D. I., & Marias, K. (2023).  
*A segmentation-based method improving the performance of N4 bias field correction on T2-weighted MR imaging data of the prostate.*  
Magnetic Resonance Imaging, 101, 1–12.**

### BibTeX
```bibtex
@article{dovrou2023segmentation,
  title={A segmentation-based method improving the performance of N4 bias field correction on T2weighted MR imaging data of the prostate},
  author={Dovrou, Aikaterini and Nikiforaki, Katerina and Zaridis, Dimitris and Manikis, Georgios C and Mylona, Eugenia and Tachos, Nikolaos and Tsiknakis, Manolis and Fotiadis, Dimitrios I and Marias, Kostas},
  journal={Magnetic Resonance Imaging},
  volume={101},
  pages={1--12},
  year={2023},
  publisher={Elsevier}
}
