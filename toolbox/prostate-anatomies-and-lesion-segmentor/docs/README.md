## Summary

The Prostate Anatomies and Lesion Segmentor produces whole-gland (WG),
peripheral-zone (PZ) and transition-zone (TZ) segmentations of the prostate from
T2-weighted MRI using a cascaded nnU-Net v2: a first network localises the whole
gland, a second segments the zones within it. When matching ADC and DWI
sequences are present, a third model (ProLesA-Net, a multi-attention network
over T2 + ADC + DWI) additionally segments prostate lesions.

The tool reads either a DICOM series tree in EUCAIM CDM layout or NIfTI volumes
laid out per patient, and writes per-case binary masks, optional probability
maps, an optional multi-segment DICOM-SEG, and a `results.json` index.

The lesion stage is skipped automatically when ADC and DWI are not available for
a case; the anatomy segmentation still runs on T2 alone.

### Hardware

A CUDA-capable GPU is strongly recommended. The container also runs on CPU with
`--device cpu`, but nnU-Net 3d_fullres inference is substantially slower there.

### Contacts

* Dimitrios Zaridis, dimzaridis@gmail.com

### Links

* [Source repository](https://github.com/dzaridis/Prostate-Anatomies-and-Lesion-Segmentor)
* nnU-Net v2: F. Isensee et al., "nnU-Net: a self-configuring method for deep
  learning-based biomedical image segmentation", Nature Methods 18, 203-211 (2021).
