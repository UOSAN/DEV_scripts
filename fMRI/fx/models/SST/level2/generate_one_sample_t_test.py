import pandas as pd
import os
from glob import glob
from level2_utils import get_data_for_confirmed_train_subjs
beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")

#paths
nonbids_data_path = "/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/"
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path ='/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts'
ml_scripting_path = dev_scripts_path + "/fMRI/ml"

train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = "/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/spmT_0001.nii",
    nonbids_data_path = nonbids_data_path,
    ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path
)

[print(s) for s in train_betas_with_data.spm_output_path_description]
