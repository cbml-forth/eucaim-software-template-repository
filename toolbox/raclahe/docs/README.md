## Summary

RACLAHE (Region Adaptive Contrast Limited Adaptive Histogram Equalization) is an
image enhancement method for T2-Weighted MR images of the prostate. A U-Net
first predicts a bounding box around the prostate, CLAHE is then applied only
within that region, and the enhanced region is recombined with the untouched
surroundings. The method was designed to improve the performance of downstream
CNN-based segmentation of the prostate and the prostatic zones (transitional and
peripheral).

The tool reads a directory holding one sub-directory per patient, where each
patient sub-directory contains either a DICOM series or a single NIfTI volume,
and writes the enhanced studies in the same format.

This module targets T2-Weighted prostate MR. Applying it to other anatomies or
sequences is not supported and the bounding-box prediction is not expected to be
meaningful there.

### Contacts

* James Zaridis, dimzaridis@gmail.com

### Links

* D. Zaridis et al., [Region-adaptive magnetic resonance image enhancement for improving CNN-based segmentation of the prostate and prostatic zones](https://doi.org/10.1038/s41598-023-27671-8), Scientific Reports 13, 714 (2023).
* [Source repository](https://github.com/dzaridis/RACLAHE_Image_Enhancement_for_CNN_model_segmentation)
