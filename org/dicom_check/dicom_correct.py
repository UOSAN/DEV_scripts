import pandas as pd
import nibabel as nib
import shutil
import os


#read in the csv file, setting a custom header since there is none in the csv
df_runs = pd.read_csv('runs_to_reset.csv', header=None, names=['subid', 'runid'])

bids_path = '/gpfs/projects/sanlab/shared/DEV/bids_data/'


for row in df_runs.itertuples():
    #get the subject id and run id
    subid = row.subid
    runid = row.runid
    
    #get the filepath to the nifti file
    img_folder = bids_path + f'sub-{subid}/ses-{runid}/func/'

    #get a list of the nifti files in the folder
    if os.path.exists(img_folder):
        img_files = [f for f in os.listdir(img_folder) if f.endswith('.nii.gz')]
    else:
        print(f'No folder found for sub-{subid} run-{runid}')
        continue
    #print the number of images found.
    print(f'Found {len(img_files)} images for sub-{subid} run-{runid}')


    #make a backup folder
    backup_folder = img_folder.replace('bids_data/',f'bids_data/derivatives/affine_correction_originals/')
    run_backup_folder = backup_folder + f'sub-{subid}/ses-{runid}/func/'
    if not os.path.exists(run_backup_folder):
        os.makedirs(run_backup_folder)

    #loop through the nifti files
    for img_file in img_files:
        #get the full filepath
        img_filepath = os.path.join(img_folder, img_file)
        #make a backup copy of the image
        shutil.copy(img_filepath, img_filepath.replace(bids_path, backup_folder))
        #load the nifti file
        img = nib.load(img_filepath)
        #get the affine matrix
        affine = img.header.get_base_affine()
        #reset the affine matrix
        newimg = nib.Nifti1Image(img.get_fdata(), affine)
        #save the file
        newimg.to_filename(img_filepath)
        
        
import nibabel as nib
import glob
import os
import glob
import datetime

#want to print and log to a log file at the same time.
#set up a function that will do this
#pass args and kwargs to the print function
def print_and_log(message, end="\n", *args, **kwargs):
    print(message, end=end, *args, **kwargs)
    with open("bids_modify.log", "a") as f:
        f.write(str(message) + end)


#print the current datetime
print_and_log("Running modification script at " + str(datetime.datetime.now()))

#check out the dicom files and see what their units are

# itentify nii.gz files.
files_to_modify = glob.glob("bids_data/sub-DEV*/ses-wave*/func/sub-DEV*_ses-wave*_bold.nii.gz")
files_to_modify.sort()
for i, fp in enumerate(files_to_modify):
    print_and_log(".", end="")
    img = nib.load(fp)
    if img.header.get_xyzt_units() != ('mm', 'sec'):
        print_and_log("\n")
        print_and_log(fp + " xytz units are not in mm and sec. Currently units are:")
        print_and_log(img.header.get_xyzt_units())
        print_and_log("Modifiying...",end="")
        img.header.set_xyzt_units('mm', 'sec')
        img.to_filename(fp)
        print_and_log("Successfully modified xytz units to mm and sec")

print_and_log("Complete.")

