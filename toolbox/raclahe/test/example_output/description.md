# Expected output

## What is in this directory

```text
example_output/
├── description.md
└── RACLAHE OUTPUT/
    └── patient-001/
        └── patient-001.nii.gz
```

The tool always creates a `RACLAHE OUTPUT` sub-directory inside the requested
output directory, then one sub-directory per processed patient. The output file
is named after the **patient directory**, not after the input file, so
`patient-001/11_axt2.nii.gz` becomes `patient-001/patient-001.nii.gz`.

## Reproducing

```bash
docker run --rm \
  -v "$PWD/test/example_input:/data/in:ro" \
  -v "$PWD/test/example_output:/data/out" \
  harbor.eucaim.cancerimage.eu/processing-tools/raclahe:3.0-fem \
  -i /data/in -o /data/out
```

## Why this output is not bit-for-bit deterministic

The pipeline runs a U-Net (TensorFlow 2.2.0) to predict the prostate bounding
box. Floating-point reductions differ between CPU microarchitectures, thread
counts and BLAS backends, so the bounding box can shift by a pixel and the
enhanced values change in the last decimals. The committed NIfTI is therefore a
**reference**, not a checksum target.

For the record, the committed file is:

| Property | Value |
| --- | --- |
| sha256 | `030dfa2338d6cae63f244f804ab04c0092344efe2e9f6200e52eb6bbac9ed47d` |
| size | 5638445 bytes |

## What an integration test should assert

Given `test/example_input/` as input, a successful run must satisfy all of the
following.

### 1. Exit code

`0`. The tool exits non-zero only when it could not process a single study.

### 2. Files

* `RACLAHE OUTPUT/patient-001/patient-001.nii.gz` exists and is a readable
  NIfTI volume.

### 3. Geometry and type

| Property | Input | Expected output |
| --- | --- | --- |
| shape (slices, rows, cols) | `(30, 512, 512)` | `(30, 256, 256)` |
| dtype | `int16` | `float64` |
| value range | `[0, 2049]` | `[0.0, 2.0]` |

The in-plane resize to 256x256 is inherent to the method: the bounding-box U-Net
takes a 256x256 input. The output range is `[0, 2]` because the CLAHE-enhanced
region and the untouched surrounding region are summed, each in `[0, 1]`.

### 4. The enhancement actually happened

`utils/Raclahe_Process.py` catches failures in the enhancement step and silently
falls back to returning the **unenhanced** image, so "a file was produced" is not
sufficient. Compare the output against the pipeline's own preprocessing of the
input (per-slice resize to 256x256, then per-slice min-max normalisation):

| Check | Reference value | Suggested tolerance |
| --- | --- | --- |
| `mean(abs(output - preprocessed_input))` | `0.0575` | `> 0.01` |
| share of pixels differing by `> 0.01` | `16.8 %` | `> 5 %` |
| histogram entropy, 64 bins over `[0, 1]` | in `5.265` -> out `5.449` | output entropy `>` input entropy |

The entropy increase is the signature of CLAHE redistributing intensities. A run
that fell back to the unenhanced image scores `0.0` on the first two rows and
leaves entropy unchanged.

### 5. Expected log

```text
Reading input studies from /data/in ..
Found 1 patient directories
== Initiating RACLAHE for study: /data/in/patient-001
patient-001 nifti saved succesfully
** Completed RACLAHE enhancement for patient-001
RACLAHE finished: 1 succeeded, 0 failed, output written to /data/out/RACLAHE OUTPUT
```

The `entrypoint.sh` lines reporting the runtime user are written to stderr and
precede this output.

### 6. Ownership

Output files must be owned by `HOST_UID:HOST_GID` when the platform injects
them, and by `1000:1000` otherwise. Nothing may be owned by root.
