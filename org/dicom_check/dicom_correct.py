import pandas as pd
import nibabel as nib
import shutil
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

print_and_log("Running modification script at " + str(datetime.datetime.now()))




#read in the csv file, setting a custom header since there is none in the csv
df_runs = pd.read_csv('runs_to_reset.csv', header=None, names=['subid', 'runid'])

bids_path = '/gpfs/projects/sanlab/shared/DEV/bids_data/'
#bids_path =  '/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/'

for row in df_runs.itertuples():
    #get the subject id and run id
    subid = row.subid
    runid = row.runid
    
    #get the filepath to the nifti file
    img_folder = bids_path + f'sub-{subid}/ses-{runid}/*/'

    #get a list of the nifti files in the folder
    #if os.path.exists(img_folder):
        #img_files = [f for f in os.listdir(img_folder) if f.endswith('.nii.gz')]
    img_files = [f for f in glob.glob(img_folder + "*.nii.gz")]
    if len(img_files) == 0:
        print_and_log(f'No folder found for sub-{subid} run-{runid}')
        continue
    #print the number of images found.
    print_and_log(f'Found {len(img_files)} images for sub-{subid} run-{runid}')


    #make a backup folder
    backup_folder = img_folder.replace('bids_data/',f'bids_data/derivatives/affine_correction_originals/')
    for bf in ['func','anat','fmap']:
        run_backup_folder = backup_folder + f'sub-{subid}/ses-{runid}/' + bf + '/'
        if not os.path.exists(run_backup_folder):
            os.makedirs(run_backup_folder)

    #loop through the nifti files
    for img_filepath in img_files:
        print_and_log(img_filepath)
        #get the full filepath
        #img_filepath = os.path.join(img_folder, img_file)
        #make a backup copy of the image
        backup_filepath =img_filepath.replace(bids_path, backup_folder)
        shutil.copy(img_filepath, backup_filepath)
        print_and_log("backup of original file saved at "+ backup_filepath)
        #load the nifti file
        img = nib.load(img_filepath)
        #get the affine matrix  
        img.header.set_sform(img.header.get_base_affine())

        img.affine[:] = img.header.get_base_affine()
        print_and_log("affine set")
        print_and_log("xyzt_units: " + str(img.header.get_xyzt_units()))
        #save the file
        img.to_filename(img_filepath)
        #want to somehow do a check as well
        print_and_log("file saved")
        

        
print_and_log("Complete.")