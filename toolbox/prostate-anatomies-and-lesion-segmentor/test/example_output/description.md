# Expected output

## Why this directory has no committed masks

The output of this tool is **not deterministic** and the masks are large, so
only this description is committed. Two sources of variation:

1. nnU-Net v2 inference on GPU uses non-deterministic cuDNN kernels, and results
   differ between GPU models, driver versions and CPU fallback.
2. The `--device auto` default selects CUDA or CPU depending on the host, and
   the two paths do not produce identical voxels.

An integration test must therefore assert on structure and plausibility rather
than on a checksum.

## Reproducing

```bash
docker run --rm --gpus all \
  -v "$PWD/test/example_input:/data/in:ro" \
  -v "$PWD/test/example_output:/data/out" \
  harbor.eucaim.cancerimage.eu/processing-tools/prostate-anatomies-and-lesion-segmentor:2.1.0-fem \
  --input /data/in --output /data/out
```

Without a GPU, add `--device cpu` and drop `--gpus all`. Expect inference to
take substantially longer.

## The example input

One real prostate MRI study in EUCAIM CDM DICOM layout:

```text
example_input/
└── PCa-103808034543450420713903538956268257799/
    └── 1.3.6.1.4.1.58108.1.255240514937543345594640077685953653009/
        ├── t2_series/   30 *.dcm   (required)
        ├── adc_series/  30 *.dcm
        └── dwi_series/  23 *.dcm
```

Because ADC and DWI are both present, the ProLesA-Net lesion stage runs in
addition to the anatomy cascade. This is the fuller of the two code paths.

## What an integration test should assert

### 1. Exit code

`0`. The tool returns `1` when at least one case failed and `2` when the input
directory does not exist or the output directory is not writable.

### 2. Files

For the single case in `example_input`, the output directory must contain a
per-case sub-directory holding:

| File | Produced when |
| --- | --- |
| `wg_binary.nii.gz` | always |
| `pz_binary.nii.gz` | always |
| `tz_binary.nii.gz` | always |
| `lesion_binary.nii.gz` | ADC + DWI present and `--save-lesion` (default) |
| `prostate_zones_seg.dcm` | DICOM input and `--save-dicom-seg` (default) |
| `wg_probs.nii.gz`, `lesion_probs.nii.gz` | only with `--save-probs` |

plus `results.json` at the root of the output directory.

### 3. `results.json`

Valid JSON with a `cases` array of one entry, whose `status` is `"ok"` and whose
`outputs` map contains at least `wg_binary`, `pz_binary` and `tz_binary` as
paths relative to the output directory. No entry may carry an `error` key.

### 4. Masks are plausible, not empty

The silent-failure mode to guard against is a model that loads and runs but
segments nothing. For each mask:

| Check | Expectation |
| --- | --- |
| dtype | integer |
| unique values | `{0, 1}` |
| non-zero voxel count | `> 0` |
| geometry | size, spacing, origin and direction identical to the T2 volume |

Anatomical sanity, which catches a mis-wired cascade that per-file checks miss:

| Check | Expectation |
| --- | --- |
| `count(wg) > count(pz)` and `count(wg) > count(tz)` | zones sit inside the gland |
| `count(pz & tz) / count(pz \| tz)` | near 0 — the zones barely overlap |
| `count(pz \| tz)` vs `count(wg)` | same order of magnitude |
| lesion, when produced | `count(lesion) > 0` and lesion mostly inside `wg` |

### 5. Non-root ownership

Every produced file must be owned by `HOST_UID:HOST_GID` when the platform
injects them, and by `1000:1000` otherwise. Nothing may be owned by root.

### 6. Expected log shape

```text
... [INFO] prostate-anatomies-and-lesion-segmentor: Input:  /data/in
... [INFO] prostate-anatomies-and-lesion-segmentor: Output: /data/out
... [INFO] prostate-anatomies-and-lesion-segmentor: Format: auto | save_probs=False | ...
... [INFO] prostate-anatomies-and-lesion-segmentor: Scratch directory: /tmp/prostai_...
... [INFO] prostate-anatomies-and-lesion-segmentor: Wrote DICOM-SEG: .../prostate_zones_seg.dcm
... [INFO] prostate-anatomies-and-lesion-segmentor: Wrote results index: /data/out/results.json
... [INFO] prostate-anatomies-and-lesion-segmentor: Done. Processed 1 case(s), 0 failure(s).
```

The `entrypoint.sh` lines reporting the runtime user are written to stderr and
precede this output.
