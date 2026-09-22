#!/usr/bin/env python3
"""
RACLAHE - Region Adaptive Contrast Limited Adaptive Histogram Equalization.

Image enhancement for CNN-based segmentation of the prostate and prostatic
zones in T2-Weighted MR images.

@author: James Zaridis
@github: https://github.com/dzaridis/RACLAHE_Image_Enhancement_for_CNN_model_segmentation
"""

import os

os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')

import argparse
import sys
import warnings

warnings.filterwarnings("ignore")

from utils.filereader import MedicalImageReader
from utils.Raclahe_Process import Raclahe_process_nifti

# Resolved relative to this file so the app works from any working directory.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WEIGHTS = os.path.join(APP_DIR, 'bbox_weights', 'checkpoint_external.h5')


def raclahe(input_dir, output_dir, weights_path):
    """Apply the RACLAHE filter to every patient directory under input_dir."""
    print(f"Reading input studies from {input_dir} ..")

    entries = sorted(os.listdir(input_dir))
    patients = [e for e in entries if os.path.isdir(os.path.join(input_dir, e))]
    skipped = [e for e in entries if e not in patients]
    if skipped:
        print(f"Skipping {len(skipped)} non-directory entries: {', '.join(skipped)}")
    if not patients:
        print(f"WARNING: no patient directories found in {input_dir}",
              file=sys.stderr)

    print(f"Found {len(patients)} patient directories")

    succeeded, failed = 0, 0
    for patient in patients:
        patient_dir = os.path.join(input_dir, patient)
        print(f"== Initiating RACLAHE for study: {patient_dir}")
        try:
            reader = MedicalImageReader(patient_dir)
            image = reader.read_image()
            Raclahe_process_nifti(str(patient), weights_path, image,
                                  output_dir, patient_dir)
            print(f"** Completed RACLAHE enhancement for {patient}")
            succeeded += 1
        except Exception as exc:
            print(f"ERROR: RACLAHE was unable to process patient {patient}: {exc}",
                  file=sys.stderr)
            failed += 1

    print(f"RACLAHE finished: {succeeded} succeeded, {failed} failed, "
          f"output written to {os.path.join(output_dir, 'RACLAHE OUTPUT')}")
    # Non-zero only when nothing at all could be processed, so that a single
    # malformed study does not fail an otherwise good batch.
    return 1 if succeeded == 0 and patients else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RACLAHE enhancement for prostate T2-Weighted MR images.")
    parser.add_argument(
        "-i", "--input-dir", default="./input_data",
        help="Folder with one sub-directory per patient, each holding a DICOM "
             "series or a single NIfTI file [%(default)s]")
    parser.add_argument(
        "-o", "--output-dir", default="./output_data",
        help="Folder where the enhanced studies will be written [%(default)s]")
    parser.add_argument(
        "-w", "--weights", dest="weights_path", default=DEFAULT_WEIGHTS,
        help="Bounding-box U-Net weights (.h5) [%(default)s]")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        sys.exit(f"ERROR: input directory does not exist or is not a "
                 f"directory: {args.input_dir}")
    if not os.path.isfile(args.weights_path):
        sys.exit(f"ERROR: bounding-box model weights not found: "
                 f"{args.weights_path}")

    os.makedirs(args.output_dir, exist_ok=True)

    sys.exit(raclahe(args.input_dir, args.output_dir, args.weights_path))
