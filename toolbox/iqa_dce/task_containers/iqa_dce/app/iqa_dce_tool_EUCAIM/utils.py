import argparse
import os
from pathlib import Path
import pickle
import time
from dark_corner_mask import mask_two_darkest_corners
from iqm_calculation import *
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from RadiomicsExtractor import RadiomicsExtractor
import SimpleITK as sitk
from SitkReader import SitkReader
import torch

SLC_START = 0
SLC_LOWER_LIMIT = 0.3
SLC_UPPER_LIMIT = 0.7
SLC_STEP_SPARSE = 0.1
SLC_MIDDLE_LOWER_LIMIT = 0.35
SLC_MIDDLE_UPPER_LIMIT = 0.65
SLC_STEP_DENSE = 0.05
SLC_STOP = 1
NUM_SELECTED_SLICES = 12


def remove_unessesary_files(folder):
    """Deletes all files inside the specified directory."""
    folder = Path(folder)
    if folder.exists():
        for item in folder.iterdir():
            if item.is_file():
                item.unlink()


def rename_dict(d, tag):
    """Appends a suffix tag to all dataframe column names."""
    columns = list(d.columns)
    nd = {}
    for i in columns:
        nd[i] = f"{i}_{tag}"
    return nd


def code_info():
    """Prints tool banner and accepts optional verbose flag."""
    parser = argparse.ArgumentParser(
        description=(
            "----------------------------------------------------------- \n"
            "---------Image Quality Assessement Breast DCE Tool--------- \n"
            "----------------------------------------------------------- \n"
            "This program is trained to predict image quality (high = 0 / low = 1) of Breast DCE first dynamic phase images in Nifti format.\n"
            "---------------\n"
            "---Citation:---\n"
            "---------------\n"
            " If used in a research project please cite the following article:\n\n"
            " Ioannidis, G.S.; Nikiforaki, K.; Dovrou, A.; Kilintzis, V.; Kalliatakis, G.; Diaz, O.; Lekadir, K.; Marias, K. "
            "Explainable Radiomics-Based Model for Automatic Image Quality Assessment in Breast Cancer DCE MRI Data. "
            "J. Imaging 2025, 11, 417. https://doi.org/10.3390/jimaging11110417"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output."
    )
    args, _ = parser.parse_known_args()
    if args.verbose:
        print("Verbose mode is on!")


def folder_structure_check_new(path):
    """Recursively scans the provided directory for files ending in '_0001.nii.gz'.

    Logs a warning for skipped files and works across root and nested
    subfolders.

    Returns:
        tuple: (status_code: int, patient_files_map: dict[str, Path])
    """
    path = Path(path)
    if not path.exists():
        print(f"Directory not found: {path}")
        return 0, {}

    # 1. Collect all files across root and subfolders
    all_files = sorted([f for f in path.rglob("*") if f.is_file()])

    valid_files = []
    skipped_files = []

    for f in all_files:
        # Check matching suffix
        if f.name.endswith("_0001.nii.gz"):
            valid_files.append(f)
        else:
            skipped_files.append(f)

    # 2. Print warning for skipped files
    if skipped_files:
        print(f"\n[!] Warning: Found {len(skipped_files)} non-target file(s):")
        for f in skipped_files:
            rel_path = f.relative_to(path)
            print(f"    - '{rel_path}' was found on input folder but skipped")
        print()

    # 3. Check if any valid target files were found
    if not valid_files:
        print(
            "No data. Please add images ending with '_0001.nii.gz' "
            "in the input folder or its subfolders."
        )
        return 0, {}

    # 4. Map patient IDs to their relative/absolute paths
    patient_files_map = {}
    for f in valid_files:
        patient_id = f.name.replace("_0001.nii.gz", "")
        if patient_id in patient_files_map:
            print(
                f"[!] Warning: Duplicate patient ID '{patient_id}' detected:\n"
                f"    Existing: {patient_files_map[patient_id]}\n"
                f"    New:      {f}\n"
                f"    Using the newer path."
            )
        patient_files_map[patient_id] = f

    print(
        f"[*] Found {len(patient_files_map)} valid DCE volume(s) across input directory."
    )
    return 1, patient_files_map


def post_process_dfs(all_features_df_full, all_features_df_bg):
    """Cleans up raw radiomics dataframes, renames background columns, and merges them."""
    all_features_df_full = all_features_df_full.drop(
        columns=["slice"], errors="ignore"
    )
    all_features_df_bg = all_features_df_bg.drop(
        columns=["slice"], errors="ignore"
    )

    all_features_df_full = all_features_df_full.dropna(axis=1)
    all_features_df_full = all_features_df_full.sort_index()

    all_features_df_bg = all_features_df_bg.dropna(axis=1)
    all_features_df_bg = all_features_df_bg.sort_index()

    new_cols = rename_dict(all_features_df_bg, "bg")
    all_features_df_bg.rename(columns=new_cols, inplace=True)

    test_data = pd.concat([all_features_df_full, all_features_df_bg], axis=1)

    return all_features_df_full, all_features_df_bg, test_data


def read_pickle(filename):
    """Loads a serialized pickle model file."""
    with open(filename, "rb") as handle:
        return pickle.load(handle)


def background_roi_creation(patient_files_map, path_masks=Path("./masks")):
    """Generates background masks for all detected patient volumes."""
    path_masks = Path(path_masks)
    path_masks.mkdir(parents=True, exist_ok=True)

    mask2d = None
    for patient_id, file_path in patient_files_map.items():
        out_path = os.path.join(path_masks, patient_id)
        mask2d, mask3d, means = mask_two_darkest_corners(
            str(file_path),
            crop_fraction=1 / 8,
            show_plots=False,
            save_mask=True,
            save_3d_mask=False,
            output_path=out_path,
        )
    return mask2d


def select_slices(image: NDArray):
    """Select 12 slices from a sequence (densely in the middle, sparsely near the edges)."""
    num_slices = image.shape[0]

    lower_range = [
        int(i * num_slices)
        for i in np.arange(SLC_START, SLC_LOWER_LIMIT, SLC_STEP_SPARSE)
    ]
    middle_range = [
        int(i * num_slices)
        for i in np.arange(
            SLC_MIDDLE_LOWER_LIMIT,
            SLC_MIDDLE_UPPER_LIMIT - 0.00001,
            SLC_STEP_DENSE,
        )
    ]
    upper_range = [
        int(i * num_slices)
        for i in np.arange(SLC_UPPER_LIMIT, SLC_STOP - 0.00001, SLC_STEP_SPARSE)
    ]

    idxs = np.concatenate((lower_range, middle_range, upper_range))
    return image[idxs], idxs


def extract_radiomics_per_slice(image: NDArray, mask: NDArray):
    """Extract and save radiomic features in a 2D image slice."""
    radiomics_extractor = RadiomicsExtractor("./radiomicsMR.yaml")

    image_sitk = sitk.GetImageFromArray(image)
    mask_sitk = sitk.GetImageFromArray(mask)

    radiomics_vector = radiomics_extractor.extract(image_sitk, mask_sitk)
    return radiomics_vector


def get_background_mask_for_patient(
    path_masks: str | Path, patient_id: str, flip: bool = True
):
    """Loads generated 2D background masks."""
    path_masks = Path(path_masks)
    reader = SitkReader()
    p_mask = list(path_masks.glob(f"{patient_id}*"))

    if len(p_mask) != 1:
        print(f"Multiple masks or no mask found for patient ID: {patient_id}")
        raise ValueError(
            f"Expected exactly 1 mask for {patient_id}, found {len(p_mask)}"
        )

    mask = reader.read(str(p_mask[0]))
    mask = np.transpose(mask, (1, 0))
    if flip:
        mask = np.flip(mask, axis=0)

    return mask


def extract_radiomics_iqm(
    patient_files_map: dict[str, Path],
    path_masks: str | Path,
    path_out: Path | str,
    image_type: str,
    mask_type: str,
):
    """Calculates radiomics and IQMs for the middle slice of each 3D image."""
    print(
        f"Starting Radiomics and IQM Extraction for {image_type} image and {mask_type} mask"
    )
    features_total_all = []
    reader = SitkReader()
    torch.manual_seed(14041931)

    start_time = time.time()
    problematic_ids = []
    problematic_slices = []

    for patient_id, path_image in patient_files_map.items():
        id = str(patient_id)
        image_3d = reader.read(str(path_image))

        # z-score normalization
        normalized_img = []
        for i in range(image_3d.shape[0]):
            slice_std = np.std(image_3d[i])
            if slice_std == 0:
                normalized_img.append(image_3d[i] - np.mean(image_3d[i]))
            else:
                normalized_img.append(
                    (image_3d[i] - np.mean(image_3d[i])) / slice_std
                )
        normalized_img = np.asarray(normalized_img)

        # select slices
        selected_slices, idxs = select_slices(normalized_img)
        middle_slice = selected_slices.shape[0] // 2

        # get mask
        if mask_type == "full":
            breast_mask = np.ones_like(image_3d)
            breast_mask[:, 0, :] = 0
            breast_mask[:, -1, :] = 0
        elif mask_type == "background":
            try:
                background_mask = get_background_mask_for_patient(
                    Path(path_masks), id, flip=False
                )
                excluded_ids = ["ISPY2_432114", "ISPY2_745633", "NACT_30"]
                if (id in excluded_ids) or (not np.any(background_mask)):
                    continue
            except Exception as e:
                print(f"Exception {e} for patient {id} while getting its mask")
                continue
        else:
            print(f"Unknown mask type: {mask_type}")
            continue

        slice = middle_slice
        failures = 0
        image = selected_slices[slice]
        if mask_type == "background":
            mask = background_mask
        elif (mask_type == "full") or (mask_type == "breast"):
            mask = breast_mask[idxs[slice], :, :]

        if image.shape != mask.shape:
            mask = mask.T
            print(
                f"Mismatch dimension error between image and breast mask for patient {id} and slice {idxs[slice]}, \n ...corrected, proceeding normally"
            )

        print(
            f"Calculating image quality metrics (NR) for patient {id} | slice {idxs[slice]}"
        )
        try:
            masked_image = image * mask
            masked_image = np.expand_dims(masked_image, axis=0)
            image_tensor = prepro(masked_image)
            nr_metrics = calculate_nr_metrics(image_tensor)
        except Exception as e:
            problematic_ids.append(id)
            problematic_slices.append(slice)
            print(
                f"Patient with id {id} and slice {idxs[slice]} failed during iqm calculation. Error:\n{e}"
            )
            failures += 1

        print(f"Calculating radiomics for patient {id} | slice {idxs[slice]}")
        try:
            image_scaled = image * 100
            radiomics_vector = extract_radiomics_per_slice(image_scaled, mask)
            radiomics_vector = {
                "patient_id": id,
                "slice": idxs[slice],
                **radiomics_vector,
            }
        except Exception as e:
            problematic_ids.append(id)
            problematic_slices.append(slice)
            print(
                f"Patient with id {id} and slice {idxs[slice]} failed during radiomics calculation. Error:\n{e}"
            )
            failures += 1

        if failures == 2:
            continue

        all_features = {**radiomics_vector, **nr_metrics}
        features_total_all.append(all_features)

    print(
        f"Radiomics extraction and IQM calculation completed in {(time.time() - start_time):.4f} seconds"
    )
    return features_total_all