# Prostate Anatomies and Lesion Segmentor

Whole-gland, zonal (PZ/TZ) and lesion segmentation from prostate MRI using a
cascaded nnU-Net v2 plus ProLesA-Net.

Submitted to the EUCAIM toolbox following [tool_template](../../tool_template/README.md).

## Contents

```text
prostate-anatomies-and-lesion-segmentor/
├── README.md
├── LICENSE
├── task_containers/
│   └── prostate-segmentor/
│       ├── dockerfile
│       ├── entrypoint.sh
│       └── app/
│           ├── __main__.py
│           ├── healthcheck.py
│           ├── Utils/
│           ├── requirements.txt
│           └── README.md
├── metadata/
│   └── FEM/
│       ├── prostate-segmentor.cwl
│       └── prostate-segmentor-bundle.cwl
├── docs/
│   └── README.md
└── test/
    ├── example_input/
    └── example_output/
```

## Task container

A single task container, `prostate-segmentor`.

| Item | Value |
| --- | --- |
| Harbor image | `harbor.eucaim.cancerimage.eu/processing-tools/prostate-anatomies-and-lesion-segmentor:2.1.0-fem` |
| Base image | `nvcr.io/nvidia/cuda:11.7.0-cudnn8-runtime-ubuntu20.04` |
| Platform | `linux/amd64` |
| GPU | CUDA 11.7, compute capability 6.0+, 1 device (CPU fallback via `--device cpu`) |
| Working directory | `/app` |
| Entrypoint | `/app/entrypoint.sh` (unmodified platform script) |
| Default command | `--input /app/input_data --output /app/output_data` |
| Runtime user | non-root, dynamic UID/GID via `HOST_UID` / `HOST_GID` / `HOST_USER` |

Build:

```bash
cd task_containers/prostate-segmentor
docker build --platform linux/amd64 -f dockerfile -t prostate-segmentor:2.1.0-fem .
```

The model weights are downloaded during the build and verified against their
SHA-256; see [Model weights](#model-weights).

## Input and output

Input is either a DICOM tree in EUCAIM CDM layout or NIfTI volumes per patient:

```text
input_data/                          input_data/
└── <patient>/                       └── <patient>/
    └── <study>/                         ├── t2_series.nii.gz
        ├── t2_series/  *.dcm            ├── adc_series.nii.gz
        ├── adc_series/ *.dcm            └── dwi_series.nii.gz
        └── dwi_series/ *.dcm
```

Only the T2 series is required. ADC and DWI enable the ProLesA-Net lesion stage;
without them the anatomy segmentation still runs and the lesion stage is skipped.

Output is one sub-directory per case containing the binary masks, optionally
probability maps and a multi-segment DICOM-SEG, plus a `results.json` index
listing every case, its status and the files produced.

## Metadata

`metadata/FEM/prostate-segmentor.cwl` is the `FEMTask` descriptor and
`metadata/FEM/prostate-segmentor-bundle.cwl` the `FEMBundle` wrapping it as a
standalone execution unit. The task declares a `CUDARequirement` alongside its
CPU and RAM minima.

User-facing inputs: `input_dir` (`--input`), `output_dir_name` (`--output`),
`input_format`, `device`, `lesion_threshold` and `save_probs`.

## Test data

`test/example_input/` holds one real prostate MRI study in EUCAIM CDM DICOM
layout, with T2 (30 slices), ADC (30) and DWI (23) series, so the lesion stage
is exercised as well as the anatomy cascade.
`test/example_output/description.md` documents what an integration test should
assert; the output is not bit-for-bit deterministic.

## Model weights

The nnU-Net and ProLesA-Net weights are **not stored in this repository**.

This repository is a public fork of `EUCAIM/software-template-repository`, and
GitHub accounts a fork's Git LFS objects against the *parent* repository's
storage, refusing LFS uploads from public forks. The weights are also 1.1 GB in
total, far above GitHub's 100 MB per-file limit for ordinary git objects.

They are published instead as a GitHub Release asset of the source repository,
which is unmetered, and fetched during the image build:

| Property | Value |
| --- | --- |
| Asset | `segmentor-weights.tar.gz` |
| Size | 1 070 717 758 bytes |
| SHA-256 | `11d3039f6841a4769c6222e27164e0fe8bcaba45e4fae205cfd38df7e48272f5` |
| Contents | `nnUNet_results/` and `lesion/`, extracted to `/opt/models` |

Point the build at a different location with:

```bash
docker build --platform linux/amd64 -f dockerfile \
  --build-arg SEGMENTOR_WEIGHTS_URL=<url> -t prostate-segmentor:2.1.0-fem .
```

Nothing is downloaded at **run** time; the weights are baked into the image.

## License

European Union Public Licence (EUPL) v1.2 — see [LICENSE](LICENSE).

## Contact

Dimitrios Zaridis, FORTH — dimzaridis@gmail.com
