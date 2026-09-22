# RACLAHE Image Enhancement

Region Adaptive Contrast Limited Adaptive Histogram Equalization (RACLAHE) for
improving CNN-based segmentation of the prostate and prostatic zones in
T2-Weighted MR images.

Submitted to the EUCAIM toolbox following [tool_template](../../tool_template/README.md).

## Contents

```text
raclahe/
├── README.md
├── LICENSE
├── task_containers/
│   └── raclahe/
│       ├── dockerfile
│       ├── entrypoint.sh
│       └── app/
│           ├── raclahe.py
│           ├── utils/
│           ├── bbox_weights/
│           ├── pyproject.toml
│           ├── uv.lock
│           └── README.md
├── metadata/
│   └── FEM/
│       ├── raclahe.cwl
│       └── raclahe-bundle.cwl
├── docs/
│   └── README.md
└── test/
    ├── example_input/
    └── example_output/
```

## Task container

A single task container, `raclahe`.

| Item | Value |
| --- | --- |
| Harbor image | `harbor.eucaim.cancerimage.eu/processing-tools/raclahe:latest` |
| Base image | `python:3.8-slim` (TensorFlow 2.2.0 publishes no wheels for Python 3.9+) |
| Platform | `linux/amd64` |
| Working directory | `/raclahe` |
| Entrypoint | `/raclahe/entrypoint.sh` (unmodified platform script) |
| Default command | `--input-dir ./input_data --output-dir ./output_data` |
| Runtime user | non-root, dynamic UID/GID via `HOST_UID` / `HOST_GID` / `HOST_USER` |

Build:

```bash
cd task_containers/raclahe
docker build --platform linux/amd64 -f dockerfile -t raclahe:3.0 .
```

The model weights are downloaded during the build and verified against their
SHA-256 checksum; see [Model weights](#model-weights) below.

## Input and output

Input is a directory holding **one sub-directory per patient**. Each patient
sub-directory contains either a DICOM series (`*.dcm`, one file per slice) or
exactly one NIfTI file (`*.nii` / `*.nii.gz`). Files directly under the input
directory are ignored.

```text
input_data/
├── patient-001/
│   └── 11_axt2.nii.gz
└── patient-002/
    ├── slice001.dcm
    └── ...
```

Output is written under `<output-dir>/RACLAHE OUTPUT/<patient>/`, in the same
format as the corresponding input.

## Metadata

`metadata/FEM/raclahe.cwl` is the `FEMTask` descriptor and
`metadata/FEM/raclahe-bundle.cwl` the `FEMBundle` wrapping it as a standalone
execution unit.

The task exposes two user inputs, `input_dir` (`-i`) and `output_dir_name`
(`-o`), and one `Directory` output.

## Test data

`test/example_input/patient-001/` holds a real axial T2-Weighted prostate MR
volume. `test/example_output/` documents what an integration test should check —
see [test/example_output/description.md](test/example_output/description.md),
since the output is not bit-for-bit deterministic.

## Model weights

The bounding-box U-Net weights (`checkpoint_external.h5`, 415 649 984 bytes,
SHA-256 `bb6eba7922fa964188aabd2232c115445c4e94e1f41d51ccdc055585662ad8ee`) are
**not stored in this repository**.

This repository is a public fork of `EUCAIM/software-template-repository`, and
GitHub accounts a fork's Git LFS objects against the *parent* repository's
storage, refusing LFS uploads from public forks. The file is also far above
GitHub's 100 MB limit for ordinary git objects, so it cannot be committed
directly either.

The dockerfile therefore fetches the weights at build time and verifies the
checksum, which also keeps the toolbox repository small for every other tool
provider. Point the build at any location that serves the file:

```bash
docker build --platform linux/amd64 -f dockerfile \
  --build-arg RACLAHE_WEIGHTS_URL=<url> -t raclahe:3.0 .
```

For a fully offline build, serve a local copy:

```bash
python3 -m http.server 8877 --directory /path/holding/the/h5
docker build --platform linux/amd64 -f dockerfile \
  --build-arg RACLAHE_WEIGHTS_URL=http://host.docker.internal:8877/checkpoint_external.h5 \
  -t raclahe:3.0 .
```

The weights are baked into the published Harbor image, so nothing is downloaded
at **run** time.

## License

European Union Public Licence (EUPL) v1.2 — see [LICENSE](LICENSE).

## Contact

James Zaridis, FORTH — dimzaridis@gmail.com
