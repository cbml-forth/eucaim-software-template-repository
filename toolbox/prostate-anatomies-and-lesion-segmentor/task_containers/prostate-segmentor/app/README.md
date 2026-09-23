## Prostate Anatomies and Lesion Segmentor

### Abstract

Accurate delineation of the prostate and its zones underpins PI-RADS reporting,
targeted biopsy planning and radiomics. This tool chains two nnU-Net v2 models —
the first localising the whole gland on T2-weighted MRI, the second segmenting
the peripheral and transition zones within that region — and optionally applies
ProLesA-Net, a multi-attention network operating jointly on T2, ADC and DWI, to
segment prostate lesions.

## Guide

First go to the dir, eg. `cd prostate-segmentor`

Build container:

```
sudo docker build -t prostate-segmentor:2.1.0-fem -f dockerfile .
```

Run container:

```
docker run --rm --gpus all \
   -v /your/path/of/input_data:/input:ro \
   -v /your/output/folder:/output \
   prostate-segmentor:2.1.0-fem --input /input --output /output
```

Add `--device cpu` and drop `--gpus all` to run without a GPU.

### Input layouts

DICOM (EUCAIM CDM):

```
input/
└── <patient>/
    └── <study>/
        ├── t2_series/     *.dcm   (required)
        ├── adc_series/    *.dcm   (optional, needed for lesions)
        └── dwi_series/    *.dcm   (optional, needed for lesions)
```

NIfTI per patient:

```
input/
└── <patient>/
    ├── t2_series.nii.gz          (required)
    ├── adc_series.nii.gz         (optional)
    └── dwi_series.nii.gz         (optional)
```

A flat `<case_id>.nii.gz` layout is also accepted for T2-only smoke tests.

### Output

One sub-directory per case with binary masks, plus `results.json` indexing every
case, its status and the files produced.

### Options

| Flag | Description | Default |
| --- | --- | --- |
| `-i`, `--input` | Read-only input directory | required |
| `-o`, `--output` | Writable output directory | required |
| `--input-format` | `auto`, `dicom` or `nifti` | `auto` |
| `--device` | `auto`, `cuda` or `cpu` | `auto` |
| `--lesion-threshold` | Lesion probability threshold | `0.1` |
| `--save-probs` | Also write probability maps | off |
| `--save-dicom-seg` / `--no-save-dicom-seg` | DICOM-SEG export for DICOM input | on |
| `--save-lesion` / `--no-save-lesion` | Run the ProLesA-Net lesion stage | on |
| `--log-level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

### Note on the model weights

The nnU-Net and ProLesA-Net weights (~1.1 GB) are not kept in this repository.
The dockerfile downloads them during the build from a GitHub Release asset of
the source repository and verifies the SHA-256, so an ordinary `docker build`
needs no extra step. To build from a different location:

```
docker build -f dockerfile --build-arg SEGMENTOR_WEIGHTS_URL=<url> -t prostate-segmentor:2.1.0-fem .
```
