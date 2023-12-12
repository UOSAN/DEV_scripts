import pandas as pd
import os
from glob import glob
import numpy as np
from level2_utils import *
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")


#paths
# nonbids_data_path = "/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/"
# ml_data_folderpath = nonbids_data_path + "fMRI/ml"
# dev_scripts_path ='/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts'
# ml_scripting_path = dev_scripts_path + "/fMRI/ml"


config_data = read_yaml_for_host("level2/l2_config.yml")
nonbids_data_path = config_data['nonbids_data_path']
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path = config_data['dev_scripts_path']
ml_scripting_path = dev_scripts_path + "/fMRI/ml"
dropbox_datapath = config_data['dropbox_datapath']
sst_level_2_path = config_data['sst_level_2_path']
template_filepath = config_data['sst_level_2_path']
spm_path = config_data['spm_path']
analysis_name = 'conditions'

train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = nonbids_data_path + "fMRI/fx/models/SST/wave1/conditions/sub-DEV*/",
    nonbids_data_path = nonbids_data_path,
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path,
    dropbox_datapath=dropbox_datapath,
    exclude_test_subjs=False
)


data_by_ppt = pd.read_csv(dropbox_datapath + "/data_by_ppt.csv")

#now combine
