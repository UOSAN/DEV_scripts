import pandas as pd
import os
from glob import glob
import numpy as np
from level2_utils import *
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")

config_data = read_yaml_for_host("l2_config.yml")

#paths
nonbids_data_path = "/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/"
dropbox_data_path = "/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/analysis_files/data"
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path ='/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts'
ml_scripting_path = dev_scripts_path + "/fMRI/ml"

first_level_path = nonbids_data_path + "fMRI/fx/models/SST/wave1/posterror_conditions/sub-DEV*/"
sst_level_2_path = config_data['sst_level_2_path']
template_filepath = config_data['spm_l2_script_template_filepath']
spm_path = config_data['spm_path']

analysis_name = 'posterror'
train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = first_level_path,
    nonbids_data_path = nonbids_data_path,
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path,
    dropbox_datapath=dropbox_data_path,
    exclude_test_subjs=False
)


betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)

contrast_name_list = ['CorrectGoFollowing(CS>FS)','CorrectGoFollowing(FS>CS)','CS>FS(PrecedingCorrectGo)','FS>CS(PrecedingCorrectGo)']


iterate_over_l1_images_and_run_l2_scripts(
    contrast_name_list, 
    l1_images_with_paths = betas_with_contrasts, 
    analysis_name = analysis_name, 
    sst_level_2_path = sst_level_2_path, 
    template_filepath = template_filepath, 
    spm_path = spm_path,
    col_function=lambda img_name: 'contrast_' + img_name + "_fname"
    )
