#!/usr/bin/env python3
"""
@author: Eleftherios Trivizakis
@github: https://github.com/trivizakis
"""

import argparse
import os
import sys

# from skimage.io import imsave
# import mlflow
import numpy as np
import SimpleITK as sitk
import tensorflow as tf
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

from hypes_handler import HypesHandler as hh
from model_factory import DnCNN

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def hypes_generator(input_shape):
    # DEEP LEARNING HYPE-PARAMS
    params = {}
    params["batch_size"] = 1
    params["kernels"] = 64
    params["layers"] = 15
    params["lr"] = 0.005
    params["residual"] = True
    params["input_shape"] = input_shape
    params["regularizer"] = "l1_l2"
    params["reg_value"] = [1e-2, 1e-2]
    params["kernel_initializer"] = "Orthogonal"
    params["loss"] = "SDI"
    params["optimizer"] = "Adam"

    params = hh.add_loss_hypes(params)
    params = hh.add_optimizer_hypes(params)
    params = hh.add_regularizer_hypes(params)
    return params

def print_os_error(error):
    print(f"ERROR raised for '{error.filename}' : {error}", file=sys.stderr)

def denoiser(input_dir, output_dir):
    print(f"Reading input NIfTI files from {input_dir} ..")

    for root, dirs, files in os.walk(input_dir + "/", onerror=print_os_error):
        for file in files:
            # report to mlflow
            # with mlflow.start_run(run_name=name + " - Volume ID: " + file, nested=True):
            input_file = input_dir + "/" + file
            print("== Initiating denoising for volume: " + input_file)
            reader = sitk.ImageFileReader()
            reader.SetImageIO("NiftiImageIO")
            reader.SetFileName(input_file)
            reader.LoadPrivateTagsOn()
            reader.ReadImageInformation()
            nifti_volume = reader.Execute()

            # get metadata
            metadata = {}
            for key in nifti_volume.GetMetaDataKeys():
                metadata[key] = nifti_volume.GetMetaData(key)

            noisy_volume = sitk.GetArrayFromImage(nifti_volume)

            var_type = noisy_volume.dtype
            shape = noisy_volume.shape
            maximum = noisy_volume.max()
            minimum = noisy_volume.min()

            if shape[1] == shape[2] and shape[0] < shape[1]:
                print("Preparing denoising")
            elif shape[0] == shape[1] and shape[2] < shape[1]:
                noisy_volume = np.transpose(noisy_volume, (2, 0, 1))
                print("Preparing denoising.")

            # initiate parameters for the deep learning architecture
            params = hypes_generator(input_shape=(shape[1], shape[2], 1))

            # initiate the model's arcitecture
            dnconv = DnCNN(params)

            # compile the model
            dnconv.compile(loss=params["loss"], optimizer=params["optimizer"])

            # load weights
            dnconv.load_weights("denoiser.h5")

            # freeze model
            for layer in dnconv.layers:
                layer.trainable = False

            # inference for nifti volume
            denoised_volume = []
            scalar_loss = []
            for pos, noisy_image in enumerate(noisy_volume):
                img = np.expand_dims(
                    np.expand_dims(
                        ((noisy_image - minimum) / (maximum - minimum)), axis=0
                    ),
                    axis=3,
                )
                clean_prd = dnconv.predict(img, batch_size=1)
                scalar_loss.append(dnconv.test_on_batch(img))
                clean_prd = np.squeeze(clean_prd, axis=3)
                clean_img = (np.squeeze(clean_prd, axis=0) * maximum).astype(var_type)
                denoised_volume.append(clean_img)

                # print-to-png
                # clean_img_print = (np.squeeze(clean_prd,axis=0)*255.0).astype(np.uint8)
                # imsave(output_dir+"/"+file[:13]+"_"+str(pos)+"_cleaned.png", clean_img_print)

            tf.keras.backend.clear_session()

            # list to numpy array
            denoised_volume = np.stack(denoised_volume, axis=0)

            PSNR = psnr(denoised_volume, noisy_volume)
            SSIM = ssim(denoised_volume, noisy_volume)
            MSE = mse(denoised_volume, noisy_volume)

            print(f"{file} > Scalar loss", np.array(scalar_loss).mean())
            print(f"{file} > Differences Index", 1 - SSIM)
            print(f"{file} > PSNR", PSNR)
            print(f"{file} > MSE", MSE)

            final_nifti = sitk.GetImageFromArray(denoised_volume)

            # set metadata to denoised image (nifti)
            for key in list(metadata.keys()):
                final_nifti.SetMetaData(key, metadata[key])

            writer = sitk.ImageFileWriter()
            writer.SetImageIO("NiftiImageIO")
            out_file = output_dir + "/" + file
            writer.SetFileName(out_file)
            writer.Execute(final_nifti)

            print(f"** Completed volume denoising {file} output saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-dir", help="Folder with the input NIfTI files [%(default)s]", default="./input_data")
    parser.add_argument("-o", "--output-dir", help="Folder where the output files will be written [%(default)s]", default="./output_data")
    args = parser.parse_args()

    denoiser(args.input_dir, args.output_dir)
