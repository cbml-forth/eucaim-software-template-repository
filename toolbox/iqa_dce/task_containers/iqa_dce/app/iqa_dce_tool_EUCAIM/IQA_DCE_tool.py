import argparse
from datetime import datetime
import os
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from utils import (
    background_roi_creation,
    code_info,
    extract_radiomics_iqm,
    folder_structure_check_new,
    post_process_dfs,
    read_pickle,
    remove_unessesary_files,
)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="IQA_DCE_tool.py",
        description=(
            "---------Image Quality Assessement Breast DCE Tool--------- \n"
            "----------------------------------------------------------- \n"
            "This program is trained to predict image quality (high = 0 / low = 1) of Breast DCE first dynamic pass images in Nifti format.\n\n"
            "---------------\n"
            "---Citation:---\n"
            "---------------\n"
            " If used in a research project please cite the following article:\n\n"
            " Ioannidis, G.S.; Nikiforaki, K.; Dovrou, A.; Kilintzis, V.; Kalliatakis, G.; Diaz, O.; Lekadir, K.; Marias, K. "
            "Explainable Radiomics-Based Model for Automatic Image Quality Assessment in Breast Cancer DCE MRI Data. "
            "J. Imaging 2025, 11, 417. https://doi.org/10.3390/jimaging11110417"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=None,
        help="Input folder path. Falls back to default if omitted or non-existent. Default /home/inputFolder",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output folder path. Created in the container if it does not exist. Default same as input folder",
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        default="",
        help='Output filename. Defaults to "IQA_predictions_<timestamp>.csv" if omitted.',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # --- 1. Handle Input Folder (-i) ---
    default_patients = Path("./inputFolder")
    if args.input:
        provided_input = Path(args.input)
        path_patients = (
            provided_input if provided_input.exists() else default_patients
        )
    else:
        path_patients = default_patients

    # --- 2. Handle Output Folder (-o) ---
    default_out = path_patients #defaults to input folder
    path_out = Path(args.output) if args.output else default_out
    path_out.mkdir(parents=True, exist_ok=True)

    # --- 3. Handle Output Filename (-f) ---
    output_filename = args.filename.strip() if args.filename else ""

    print(f"[*] Input Path:  {path_patients.resolve()}")
    print(f"[*] Output Path: {path_out.resolve()}")
    print(
        f"[*] Filename:    {output_filename if output_filename else '[Auto-generate with timestamp]'}"
    )

    path_masks = Path("./masks")
    path_masks.mkdir(parents=True, exist_ok=True)

    # Recursive check: returns (1/0, dict of {patient_id: absolute_path})
    status, patient_files_map = folder_structure_check_new(path_patients)

    if status == 1 and patient_files_map:
        print("------------Creating Background Masks------------")
        _ = background_roi_creation(patient_files_map, path_masks=path_masks)

        print(
            "------------Extracting Radiomic features from Whole image------------"
        )
        features_total_all = extract_radiomics_iqm(
            patient_files_map=patient_files_map,
            path_masks=path_masks,
            path_out=path_out,
            image_type="raw",
            mask_type="full",
        )
        all_features_df_full = pd.DataFrame.from_dict(features_total_all)
        all_features_df_full.set_index(
            all_features_df_full.columns[0], inplace=True
        )

        print(
            "------------Extracting Radiomic features from Background Masks------------"
        )
        features_total_all = extract_radiomics_iqm(
            patient_files_map=patient_files_map,
            path_masks=path_masks,
            path_out=path_out,
            image_type="raw",
            mask_type="background",
        )
        all_features_df_bg = pd.DataFrame.from_dict(features_total_all)
        all_features_df_bg.set_index(
            all_features_df_bg.columns[0], inplace=True
        )

        # Post-processing radiomic dataframes
        all_features_df_full, all_features_df_bg, test_data = post_process_dfs(
            all_features_df_full, all_features_df_bg
        )

        # Import trained model
        model = read_pickle("mama_mia_RV_retrained_model_parameters_v3.pickle")
        classifier = model["classifier"]
        scaler = model["scaler"]
        best_features = model["best_features"]

        # Data normalization & prediction
        scaled = scaler.transform(test_data)
        x_test_fold = pd.DataFrame(
            scaled, columns=test_data.columns, index=test_data.index
        )
        x_test_fold = x_test_fold[best_features]

        # --- Predictions and CSV Generation ---
        predicted = classifier.predict(x_test_fold)

        # Compute the path of each analyzed file relative to the input directory
        analyzed_relative_paths = [
            str(patient_files_map[pid].relative_to(path_patients))
            for pid in all_features_df_full.index
        ]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remove_unessesary_files(path_masks)

        if not output_filename:
            output_filename = f"IQA_predictions_{timestamp}.csv"

        # Build DataFrame directly using a dictionary to prevent formatting/delimiter issues
        prediction_df = pd.DataFrame(
            {
                "Analyzed File": analyzed_relative_paths,
                "Prediction - Low quality = 1 / Good quality =0": (
                    predicted.astype(int)
                ),
            }
        )

        save_filepath = path_out / output_filename
        prediction_df.to_csv(save_filepath, index=False)

        print(f"[*] Image quality predictions saved as CSV in: {output_filename}")
    else:
        print("Execution has stopped due to invalid folder structure or no data.")