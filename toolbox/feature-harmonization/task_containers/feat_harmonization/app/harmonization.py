"""
@author: Elisavet Stamoulou, Aikaterini Dovrou
"""

import argparse
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from neuroCombat import neuroCombat


def harmonization(
    path_in: Path,
    output_dir: Path,
    manufacturer: bool,
    manufacturer_model: bool,
    use_combat: bool,
):

    radiomics_file: Path = path_in / "radiomics.csv"
    metadata_file: Path = path_in / "metadata.csv"

    for f in [radiomics_file, metadata_file]:
        if not f.exists():
            print(f"File '{f}' does not exist in the input folder {path_in}")
            sys.exit(1)

    #  folders = glob.glob(os.path.join(path_in, "*"))

    #  input_dir_radiomics = [
    #      path for path in folders if path.split(os.sep)[-1] == "radiomics"
    #  ]
    #  if len(input_dir_radiomics) == 0:
    #      raise ValueError(
    #          "No radiomics folder found. Please create a folder with name 'radiomics', which contains a csv file with the radiomics data."
    #      )

    #  input_dir_tags = [path for path in folders if path.split(os.sep)[-1] == "metadata"]
    #  if len(input_dir_tags) == 0:
    #      raise ValueError(
    #          "No metadata folder found. Please create a folder with name 'metadata', which contains a csv file with the corresponding metadata."
    #      )

    #  # Patients = glob.glob(input_dir_dicoms+'/*')
    #  # dicom_files = []

    #  # Reading from json file
    #  # with open('ComBat_hypes.json', 'r') as openfile:
    #  #    hypes = json.load(openfile)

    #  # Read radiomics file
    #  radiomics_files = glob.glob(os.path.join(input_dir_radiomics[0], "*"))
    #  if len(radiomics_files) == 0:
    #      raise ValueError("The folder 'radiomics' is empty.")
    #  else:
    #      radiomics_file = radiomics_files[0]

    #  # Read metadata file
    #  metadata_files = glob.glob(os.path.join(input_dir_tags[0], "*"))
    #  if len(metadata_files) == 0:
    #      raise ValueError("The folder 'metadata' is empty.")
    #  else:
    #      metadata_file = metadata_files[0]

    try:
        radiomics = pd.read_csv(radiomics_file)
        radiomics = radiomics.set_index("PatientID")
        radiomics = radiomics.sort_index()
    except Exception as e:
        raise e

    try:
        covars = pd.read_csv(metadata_file)
        covars = covars.set_index("PatientID")
        covars = covars.sort_index()

        if manufacturer:
            new_covars = covars[["Manufacturer"]].copy()
        if manufacturer_model:
            new_covars = covars[["ManufacturerModelName"]].copy()
    except Exception as e:
        raise e

    radiomics = radiomics.T

    if manufacturer:
        batch_col = "Manufacturer"
    if manufacturer_model:
        batch_col = "ManufacturerModelName"

    method = {}
    if use_combat:
        print("Run ComBat method")
        ref_batch = None
        method = "ComBat"
    else:
        ref_batch = new_covars[batch_col].value_counts().idxmax()
        print("Run M_ComBat method")
        method = "M_ComBat"

    ComBat_harm = neuroCombat(
        dat=radiomics, covars=new_covars, batch_col=batch_col, ref_batch=ref_batch
    )
    harmonized_data_dataframe = pd.DataFrame(
        data=ComBat_harm["data"].T, columns=list(radiomics.T.columns)
    )
    harmonized_data_dataframe["PatientID"] = radiomics.T.index
    harmonized_data_dataframe = harmonized_data_dataframe.set_index("PatientID")

    # harmonized_data_dataframe.to_pickle(output_dir+"/harmonized_radiomics.pkl")
    harmonized_data_dataframe.to_csv(output_dir / "harmonized_radiomics.csv")

    with open(output_dir / "harmonization_estimates.pkl", "wb") as handle:
        pickle.dump(ComBat_harm["estimates"], handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(output_dir / "harmonization_info.pkl", "wb") as handle:
        pickle.dump(ComBat_harm["info"], handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("INPUT_DIR", help="Input directory")
    parser.add_argument("OUTPUT_DIR", help="Output directory")

    parser.add_argument(
        "-M",
        "--manufacturerModelName",
        dest="manufacturerModel",
        action="store_true",
        required=False,
        help=(
            "If specified, the manufacturer Model variable instead of the (default)"
            "manufacturer variable will be used as center-effect."
        ),
    )
    parser.add_argument(
        "-c",
        "--combat",
        dest="combat",
        action="store_true",
        required=False,
        help="If specified, the ComBat method will be used. If not, the M-ComBat method will be used.",
    )

    args = parser.parse_args()

    use_manufacturer_model = args.manufacturerModel
    use_manufacturer = not use_manufacturer_model

    if not os.path.isdir(args.INPUT_DIR):
        print(f"Invalid INPUT_DIR: {args.INPUT_DIR}")
        sys.exit(-1)

    path_in = Path(args.INPUT_DIR)

    if not os.path.isdir(args.OUTPUT_DIR):
        print(f"Invalid OUTPUT_DIR: {args.OUTPUT_DIR}")
        sys.exit(-1)

    path_out = Path(args.OUTPUT_DIR)

    try:
        harmonization(
            path_in,
            path_out,
            use_manufacturer,
            use_manufacturer_model,
            args.combat,
        )
    except Exception as e:
        print(e)
        sys.exit(-1)
