import pandas as pd
import os
from glob import glob
import numpy as np
from level2_utils import *
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")
#now /Users/bensmith/Documents/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/posterror_conditions_repeat3-CS-first
#beta_df['spm_l2_path_description'] =beta_df.beta_filepath
#paths
nonbids_data_path = "/Users/bensmith/Documents/data/DEV/nonbids_data/"
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path ='/Users/bensmith/Documents/code/DEV_scripts'
ml_scripting_path = dev_scripts_path + "/fMRI/ml"

train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = nonbids_data_path + "fMRI/fx/models/SST/wave1/posterror_conditions_repeat3-CS-first/sub-DEV*/",
    nonbids_data_path = nonbids_data_path,
    ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path
)

betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)

for contrast_name in ['CorrectGoFollowing(CS>FS)','CorrectGoFollowing(FS>CS)']:
    contrast_colname = 'contrast_' + contrast_name + '_fname'
    print(contrast_name)
    if contrast_colname in betas_with_contrasts.columns:
        for i, r in betas_with_contrasts.iterrows():
            if pd.isnull(r[contrast_colname]) is False:
                tmap_filepath = r.loc['spm_l2_path'] + r.loc[contrast_colname]
                print("'" + tmap_filepath + ",1'")
    else:
        print('contrast ' + contrast_name + ' not found.')


#[print(s) for s in train_betas_with_data.spm_l2_path_description]
