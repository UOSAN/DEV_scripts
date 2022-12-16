import pandas as pd
import os
from glob import glob
import numpy as np
from level2_utils import *
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")

config_data = read_yaml_for_host("l2_config.yml")
nonbids_data_path = config_data['nonbids_data_path']
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path = config_data['dev_scripts_path']
ml_scripting_path = dev_scripts_path + "/fMRI/ml"
dropbox_datapath = config_data['dropbox_datapath']
sst_level_2_path = config_data['sst_level_2_path']
template_filepath = config_data['spm_l2_script_template_filepath']
spm_path = config_data['spm_path']

analysis_name = 'posterror_conditions_w_drt'
train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = nonbids_data_path + "fMRI/fx/models/SST/wave1/" + analysis_name + "/sub-DEV*/",
    nonbids_data_path = nonbids_data_path,
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path,
    dropbox_datapath=dropbox_datapath,
    exclude_test_subjs=False
)


betas_with_paths = get_beta_fnames_for_beta_dirs(train_betas_with_data)

print(betas_with_paths.columns)

beta_name_list = [
       'CorrectGoFollowingCorrectStop',
       'CorrectGoFollowingCorrectStopxCgfcs_post_pre_drt',
       'CorrectGoFollowingFailedStop',
       'CorrectGoFollowingFailedStopxCgffs_post_pre_drt',
       'OtherCorrectGo',
       'OtherCorrectGoxOcg_post_pre_drt',
       'CorrectStopPrecedingCorrectGo',
       'CorrectStopPrecedingCorrectGoxCspcg_post_pre_drt',
       'FailedStopPrecedingCorrectGo',
       'FailedStopPrecedingCorrectGoxFspcg_post_pre_drt',
       'OtherCorrectStop',
       'OtherCorrectStopxOcs_post_pre_drt',
       'OtherFailedStop',
       'OtherFailedStopxOfs_post_pre_drt', 
       'Cue', 'CuexC_post_pre_drt', 
       'OtherFailedGo','OtherFailedGoxOfg_post_pre_drt'
    ]

iterate_over_l1_images_and_run_l2_scripts(
    beta_name_list, betas_with_paths, analysis_name, sst_level_2_path, template_filepath, spm_path,
    col_function=lambda img_name: "beta_" + img_name + "_fname"
)

