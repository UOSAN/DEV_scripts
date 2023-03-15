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