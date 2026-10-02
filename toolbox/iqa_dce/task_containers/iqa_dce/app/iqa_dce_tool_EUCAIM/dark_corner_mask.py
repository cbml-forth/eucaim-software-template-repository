import SimpleITK as sitk
import numpy as np
#import matplotlib.pyplot as plt
import os
from typing import Optional

def mask_two_darkest_corners(
    nii_path: str,
    crop_fraction: float = 1/8,
    show_plots: bool = True,
    save_mask: bool = False,
    save_3d_mask: bool = False,
    output_path: Optional[str] = None
):
    """
    Load a NIfTI volume, extract the middle axial slice,
    find the two darkest corner regions, and return 2D + 3D masks.
    Optionally saves masks as NIfTI files.
    Parameters
    ----------
    nii_path : str
        Path to the .nii or .nii.gz file.
    crop_fraction : float, optional
        Fraction of the slice to crop from each side (default = 1/8).
    show_plots : bool, optional
        If True, display the slice and mask using matplotlib.
    save_mask : bool, optional
        If True, save the 2D mask to disk as a NIfTI (.nii.gz) file.
    save_3d_mask : bool, optional
        If True, also save the 3D mask as a NIfTI (.nii.gz) file.
    output_path : str or None, optional
        Custom output path (without extension).
        If None, saves next to the input file with '_mask' suffix.
    Returns
    -------
    mask_2d : np.ndarray
        2D binary mask for the middle slice.
    mask_3d : np.ndarray
        3D binary mask (same shape as input volume).
    means : np.ndarray
        Mean intensities of the four corner regions [UL, UR, BL, BR].
    """


    # --- Load NIfTI with SimpleITK ---
    img = sitk.ReadImage(nii_path)
    vol = sitk.GetArrayFromImage(img)  # shape: [Z, Y, X]

    Z, H, W = vol.shape
    z_mid = Z // 2

    # Extract slice (convert to numpy as (H, W))
    slice2d = vol[z_mid, :, :].astype(np.float32)

    ch, cw = int(H * crop_fraction), int(W * crop_fraction)

    # --- Extract corners ---
    UL = slice2d[:ch, :cw]
    UR = slice2d[:ch, -cw:]
    BL = slice2d[-ch:, :cw]
    BR = slice2d[-ch:, -cw:]

    means = np.array([UL.mean(), UR.mean(), BL.mean(), BR.mean()])
    two_darkest = np.argsort(means)[:2]

    # --- Build 2D mask ---
    mask_2d = np.zeros_like(slice2d, dtype=np.uint8)
    if 0 in two_darkest: mask_2d[:ch, :cw] = 1
    if 1 in two_darkest: mask_2d[:ch, -cw:] = 1
    if 2 in two_darkest: mask_2d[-ch:, :cw] = 1
    if 3 in two_darkest: mask_2d[-ch:, -cw:] = 1

    # --- Expand to 3D mask ---
    mask_3d = np.zeros_like(vol, dtype=np.uint8)
    mask_3d[z_mid, :, :] = mask_2d

    # --- Optional visualization ---
    # if show_plots:
    #     plt.figure(figsize=(10, 4))
    #     plt.subplot(1, 2, 1)
    #     plt.title("Middle axial slice (Z/2)")
    #     plt.imshow(slice2d.T, cmap='gray', origin='lower')

    #     plt.subplot(1, 2, 2)
    #     plt.title("2D Mask of two darkest corners")
    #     plt.imshow(mask_2d.T, cmap='gray', origin='lower')
    #     plt.tight_layout()
    #     plt.show()

    # --- Prepare output path ---
    base, ext = os.path.splitext(nii_path)
    if ext == ".gz":
        base, _ = os.path.splitext(base)

    if output_path is None:
        output_path = base + "_mask"

    # --- Saving masks using SimpleITK ---
    if save_mask:
        # ----- SAVE 2D MASK -----
        # 2D mask stored as a 3D image with depth=1
        mask2d_itk = sitk.GetImageFromArray(mask_2d[np.newaxis, :, :])
    
        # Set 2D mask spatial info manually
        orig = list(img.GetOrigin())
        sp   = list(img.GetSpacing())
        direc = list(img.GetDirection())  # 3x3
    
        # Extract in-plane direction (2x2 block)
        dir2d = [
            direc[0], direc[1],   # row 0
            direc[3], direc[4]    # row 1
        ]
    
        # Set origin: same x,y but z must correspond to slice index
        mask2d_itk.SetOrigin([orig[0], orig[1], orig[2] + sp[2] * z_mid])
    
        # Set spacing: same as original
        mask2d_itk.SetSpacing(sp)
    
        # Set direction (2×2 expanded to 3×3)
        # Set identity direction (valid + orthonormal)
        mask2d_itk.SetDirection([1, 0, 0,
                                 0, 1, 0,
                                 0, 0, 1])
        
    
        path_2d = f"{output_path}.nii.gz"
        sitk.WriteImage(mask2d_itk, path_2d)
        print(f"2D mask saved: {path_2d}")
    
    
    
        # ----- SAVE 3D MASK -----
        if save_3d_mask:
            mask3d_itk = sitk.GetImageFromArray(mask_3d)
            mask3d_itk.CopyInformation(img)   # this one works!
            path_3d = f"{output_path}_3d.nii.gz"
            sitk.WriteImage(mask3d_itk, path_3d)
            print(f"3D mask saved: {path_3d}")



    return mask_2d, mask_3d, means

if __name__ == '__main__':
    mask2d, mask3d, means = mask_two_darkest_corners('samples/Artifacts/DUKE_040/DUKE_040_0001.nii.gz')
    print("Corner means [UL, UR, BL, BR]:", means)