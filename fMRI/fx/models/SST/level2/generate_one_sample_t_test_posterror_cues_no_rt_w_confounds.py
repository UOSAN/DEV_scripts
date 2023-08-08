import pandas as pd
import os
from glob import glob
import numpy as np
from level2_utils import get_data_for_confirmed_train_subjs, read_yaml_for_host
from level2_utils import *
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")

#beta_df['spm_l2_path_description'] =beta_df.beta_filepath
#paths
# nonbids_data_path = "/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/"
# dropbox_data_path = "/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/analysis_files/data"
# ml_data_folderpath = nonbids_data_path + "fMRI/ml"
# dev_scripts_path ='/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts'
# ml_scripting_path = dev_scripts_path + "/fMRI/ml"

config_data = read_yaml_for_host("l2_config.yml")
nonbids_data_path = config_data['nonbids_data_path']
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path = config_data['dev_scripts_path']
ml_scripting_path = dev_scripts_path + "/fMRI/ml"
dropbox_datapath = config_data['dropbox_datapath']
sst_level_2_path = config_data['sst_level_2_path']
template_filepath = config_data['spm_l2_script_w_confounders_template_filepath']
spm_path = config_data['spm_path']

analysis_name = 'posterror_cues_no_rt'
output_name = analysis_name + '_agesex'

train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = nonbids_data_path + "fMRI/fx/models/SST/wave1/" + analysis_name + "/sub-DEV*/",
    nonbids_data_path = nonbids_data_path,
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path,
    dropbox_datapath=dropbox_datapath,
    exclude_test_subjs=False
)

betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)
betas_with_paths = get_beta_fnames_for_beta_dirs(train_betas_with_data)


print(betas_with_contrasts.columns)
contrast_name_list = [
    'CueFollowing(CS>FS)',
    'CueFollowing(FS>CS)',
    'CorrectGoFollowing(CS>FS)',
    'CorrectGoFollowing(FS>CS)'
    #we can't contrast CG and CS because
    #we haven't prepared t-maps properly
    #considering that some cue items will be missing and the betas won't be in the same order
]

iterate_over_l1_images_and_run_l2_scripts(
    contrast_name_list, betas_with_contrasts, output_name, sst_level_2_path, template_filepath, spm_path,
    col_function=lambda img_name: "contrast_" + img_name + "_fname",
    confounders=['age365','birthsex'],
    confounder_template_path = config_data['confounder_template_path'],
    consess_template_path=config_data['confounder_consess_template_path'],
    conspec_template_path=config_data['confounder_conspec_template_path']
)



print(betas_with_paths.columns)

beta_name_list = [
    'CorrectGoFollowingCorrectStop',
    'CorrectGoFollowingFailedStop',
    'CueFollowingCorrectStop',
    'CueFollowingFailedStop'
    ]

iterate_over_l1_images_and_run_l2_scripts(
    beta_name_list, betas_with_paths, output_name, sst_level_2_path, template_filepath, spm_path,
    col_function=lambda img_name: "beta_" + img_name + "_fname",
    confounders=['age365','birthsex'],
    confounder_template_path = config_data['confounder_template_path'],
    consess_template_path=config_data['confounder_consess_template_path'],
    conspec_template_path=config_data['confounder_conspec_template_path']

)

