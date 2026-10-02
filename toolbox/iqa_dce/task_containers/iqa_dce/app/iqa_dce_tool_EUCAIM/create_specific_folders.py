import os
import shutil
from pathlib import Path

# Folder containing your NIfTI files
#folder = Path('/media/geo/Elements/FOR KATERINA/iqa-dce-input-all-flat')

# # Loop through all files in the folder
# for filename in os.listdir(folder):

#     if filename.endswith(".nii.gz"):

#         # Get patient name
#         # RV_01_00036_0001.nii.gz → RV_01_00036
#         patient_name = filename.replace("_0001.nii.gz", "")

#         # Create patient folder
#         patient_folder = os.path.join(folder, patient_name)
#         os.makedirs(patient_folder, exist_ok=True)

#         # Source and destination paths
#         source = os.path.join(folder, filename)
#         destination = os.path.join(patient_folder, filename)

#         # Move the NIfTI file into the patient folder
#         shutil.move(source, destination)

#         print(f"Moved {filename} → {patient_name}/")



folder_train = Path('/media/geo/Elements/FOR KATERINA/iqa-dce-input-all-flat-train')

folder_test = Path('/media/geo/Elements/FOR KATERINA/iqa-dce-input-all-flat-test')

test_pats = [f for f in os.listdir('./images') if not f.endswith('.csv') ]

for f in os.listdir(folder_train):
    
    if f in test_pats:
        
       shutil.move(os.path.join(folder_train,f), os.path.join(folder_test,f))
       
           
           