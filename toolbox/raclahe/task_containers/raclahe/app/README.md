## RACLAHE Image Enhancement

### Abstract

Automated segmentation of the prostate and its zones on T2-Weighted MR images is
sensitive to the contrast characteristics of the acquisition. RACLAHE
(Region Adaptive Contrast Limited Adaptive Histogram Equalization) improves this
by restricting contrast enhancement to the anatomically relevant region: a U-Net
predicts a bounding box around the prostate, CLAHE is applied inside it, and the
result is recombined with the unmodified surrounding tissue. Applied as a
preprocessing step, the method improved the Dice score of CNN-based segmentation
of the whole gland and of the transitional and peripheral zones.

### Paper

D. Zaridis et al., "Region-adaptive magnetic resonance image enhancement for
improving CNN-based segmentation of the prostate and prostatic zones",
Scientific Reports 13, 714 (2023), doi: 10.1038/s41598-023-27671-8.

### keywords

{Prostate;Magnetic resonance imaging;Image enhancement;CLAHE;Segmentation;Deep
learning;U-Net;Prostatic zones}

## Guide

First go to the dir, eg. `cd raclahe`

Build container: `sudo docker build -t raclahe -f dockerfile .`

Run container:

```
docker run \
   -v /your/path/of/input_data:/input \
   -v /your/output/folder:/output \
   raclahe --input-dir /input --output-dir /output
```

eg. /your/path/of/input_data - provide the path for your data

Input: a folder with one sub-directory per patient. Each patient sub-directory
holds either a DICOM series (`*.dcm`, one file per slice) or exactly one NIfTI
file (`*.nii` / `*.nii.gz`):

```
input_data/
├── patient-001/
│   └── 11_axt2.nii.gz
└── patient-002/
    ├── slice001.dcm
    └── ...
```

Output: enhanced examinations under `output_data/RACLAHE OUTPUT/<patient>/`, in
the same format as the input (NIfTI in, NIfTI out; DICOM in, DICOM out).

### Options

| Flag | Description | Default |
| --- | --- | --- |
| `-i`, `--input-dir` | Folder with one sub-directory per patient | `./input_data` |
| `-o`, `--output-dir` | Folder where enhanced studies are written | `./output_data` |
| `-w`, `--weights` | Bounding-box U-Net weights (`.h5`) | `./bbox_weights/checkpoint_external.h5` |

### Note on the model weights

`bbox_weights/checkpoint_external.h5` (415 MB) is not kept in this repository.
The dockerfile downloads it during the build and checks its SHA-256, so an
ordinary `docker build` needs no extra step. To build from a different location:

```
docker build -f dockerfile --build-arg RACLAHE_WEIGHTS_URL=<url> -t raclahe .
```

If the weights are missing at run time the container exits non-zero with
`ERROR: bounding-box model weights not found: <path>`.
