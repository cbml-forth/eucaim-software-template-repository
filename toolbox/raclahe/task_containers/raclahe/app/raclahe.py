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

    # Exit non-zero whenever nothing was produced. An input directory holding
    # no usable sub-directories is almost always a path pointed one level too
    # deep (e.g. at a DICOM series folder rather than at its parent), and
    # exiting 0 there makes a batch run look successful while doing nothing.
    if not patients:
        print("ERROR: no patient directories found. RACLAHE expects the input "
              "directory to CONTAIN one sub-directory per patient or series, "
              "each holding the DICOM/NIfTI files directly "
              "(INPUT_DIR/<patient>/*.dcm). Point it one level higher.",
              file=sys.stderr)
        return 2
    if succeeded == 0:
        print("ERROR: no study could be processed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="raclahe",
        description="RACLAHE enhancement for prostate T2-Weighted MR images.",
        epilog="The input and output directories may be given either as flags "
               "(-i/-o, for CWL execution) or as two positional arguments "
               "(for `jobman submit -i raclahe -- <INPUT_DIR> <OUTPUT_DIR>`). "
               "Flags win if both are supplied.")
    parser.add_argument(
        "-i", "--input-dir", default=None,
        help="Folder with one sub-directory per patient, each holding a DICOM "
             "series or a single NIfTI file [./input_data]")
    parser.add_argument(
        "-o", "--output-dir", default=None,
        help="Folder where the enhanced studies will be written "
             "[./output_data]")
    parser.add_argument(
        "-w", "--weights", dest="weights_path", default=DEFAULT_WEIGHTS,
        help="Bounding-box U-Net weights (.h5) [%(default)s]")
    parser.add_argument(
        "positional", nargs="*", metavar="INPUT_DIR OUTPUT_DIR",
        help="Same two directories given positionally, as the EUCAIM "
             "application catalogue documents them.")
    args = parser.parse_args()

    # Reconcile the two accepted forms. Flags take precedence; positionals fill
    # whatever the flags left unset, so both interfaces reach the same code.
    if len(args.positional) > 2:
        parser.error(f"expected at most 2 positional arguments "
                     f"(INPUT_DIR OUTPUT_DIR), got {len(args.positional)}: "
                     f"{' '.join(args.positional)}")
    pos_in = args.positional[0] if len(args.positional) >= 1 else None
    pos_out = args.positional[1] if len(args.positional) >= 2 else None
    if args.input_dir is not None and pos_in is not None:
        print(f"WARNING: input directory given twice; using the flag "
              f"{args.input_dir!r} and ignoring {pos_in!r}", file=sys.stderr)
    if args.output_dir is not None and pos_out is not None:
        print(f"WARNING: output directory given twice; using the flag "
              f"{args.output_dir!r} and ignoring {pos_out!r}", file=sys.stderr)
    args.input_dir = args.input_dir or pos_in or "./input_data"
    args.output_dir = args.output_dir or pos_out or "./output_data"

    if not os.path.isdir(args.input_dir):
        sys.exit(f"ERROR: input directory does not exist or is not a "
                 f"directory: {args.input_dir}")
    if not os.path.isfile(args.weights_path):
        sys.exit(f"ERROR: bounding-box model weights not found: "
                 f"{args.weights_path}")

    os.makedirs(args.output_dir, exist_ok=True)

    sys.exit(raclahe(args.input_dir, args.output_dir, args.weights_path))
