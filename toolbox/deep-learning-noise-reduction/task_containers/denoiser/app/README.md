## Deep Learning Noise Reduction (DLNR)

### Abstract

Anatomical magnetic resonance images are affected by different types of noise, including thermal, motion, radio interference, and magnetic field inhomogeneities. In a clinical setting, acquiring MR images of the highest quality is not always feasible. Quantitative and artificial intelligencebased decision support tools require high-quality data to accurately differentiate among pathological conditions, avoiding diminishing the clinical relevance of a diagnostic model. A fully convolutional model with no pooling layers was trained on a set of noisy images, with the ground truth being the original image without the noise. Different levels of noise were incorporated into the training set. The experiments showed a reduction in noise levels, but it can impact quantification tasks when T2ws without noise are provided to the model. Six types of pairs of original T2w image slices and the corresponding slices with synthetic noise were generated with various thresholds of Gaussian noise, spanning from 4% to 14%. In total, 38500 pairs were utilized for convergence and evaluation of the proposed
Published in: 2025 IEEE 19th International Symposium on Applied Computational Intelligence and Informatics (SACI)

### Paper
E. Trivizakis et al., "Texture Preserving Deep Learning-Based Noise Reduction for Anatomical Magnetic Resonance Images and its Impact on Imaging Features," 2025 IEEE 19th International Symposium on Applied Computational Intelligence and Informatics (SACI), Timisoara, Romania, 2025, pp. 000223-000230, doi: 10.1109/SACI66288.2025.11030174.

### keywords
{Deep learning;Training;Pathology;Noise reduction;Magnetic resonance;Nonhomogeneous media;Thermal noise;Noise measurement;Radiomics;Noise level;deep learning;denoiser;magnetic resonance imaging;radiomics;prostate}


## Guide

First go to the dir, eg. `cd denoiser`

Build container: `sudo docker build -t denoiser .`

Run container:

```
docker run \
   -v /your/path/of/input_data:/input \
   -v /your/output/folder:/output \
   denoiser --input-dir /input --output-dir /output
```

eg. /your/path/of/input_data - provide the path for your data


Input: a folder (input_data) with MR volumes (nifti files) 

Output: denoised examinations (nifti files) with corresponding filenames (output_data)
