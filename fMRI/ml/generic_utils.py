#in this file, only do input/output stuff. 
#do not include nilearn or mvpa2. This should be accessible in environments where neither of those are installed.
#we do include nib
import os
import pandas as pd


def get_all_masks(ml_data_folderpath):

    neurosynth_mask_folder = ml_data_folderpath + "/masks/response_inhibition_related/"
    harvox_mask_folder = ml_data_folderpath + "/masks/response_inhibition_related/harvardoxford/"
    

    masks_df = pd.concat([
        get_mask_folder_df(neurosynth_mask_folder,0.1),#needs to be greater than 0. Any value 0>x>3 would do
        get_mask_folder_df(harvox_mask_folder,10)
    ])
    masks_df.reset_index(drop=True,inplace=True)
    return(masks_df)


def get_failure_masks(ml_data_folderpath):

    neurosynth_mask_folder = ml_data_folderpath + "/masks/failure_related/"
    harvox_mask_folder = ml_data_folderpath + "/masks/failure_related/harvardoxford/"
    

    masks_df = pd.concat([
        get_mask_folder_df(neurosynth_mask_folder,0.1),#needs to be greater than 0. Any value 0>x>3 would do
        get_mask_folder_df(harvox_mask_folder,10)
    ])
    masks_df.reset_index(drop=True,inplace=True)
    return(masks_df)


def get_mask_folder_df(mask_folder, thresh):
    masks = get_masks_in_folder(mask_folder)
    masks_df = pd.DataFrame({
        'mask_name':[s.replace(".nii.gz","") for s in masks],
        'mask_filepath':[mask_folder + s for s in masks],
        'thresh':thresh
    })
    return(masks_df)      
        
        
        
    
        
def get_masks_in_folder(mask_folder):
    #print(os.listdir(mask_folder))
    mask_name_list = [s for s in os.listdir(mask_folder) if os.path.isdir(mask_folder + s) is False]
        
    return(mask_name_list)