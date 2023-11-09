import pandas as pd
import os
from glob import glob
import numpy as np
from level2_utils import *
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")

#beta_df['spm_l2_path_description'] =beta_df.beta_filepath
#paths
# nonbids_data_path = "/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/"
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
template_filepath = config_data['spm_l2_script_template_filepath']
spm_path = config_data['spm_path']
analysis_name = 'conditions'

# train_betas_with_data = get_data_for_confirmed_train_subjs(
#     beta_glob = nonbids_data_path + "fMRI/fx/models/SST/all_waves/conditions/sub-DEV*/",
#     nonbids_data_path = nonbids_data_path,
#     #ml_data_folderpath = ml_data_folderpath,
#     ml_scripting_path = ml_scripting_path,
#     dropbox_datapath=dropbox_datapath,
#     exclude_test_subjs=False
# )

train_betas_with_data = get_sst_subj_folder_paths_for_subjs_w_two_sessions(
    beta_glob = nonbids_data_path + "fMRI/fx/models/SST/all_waves/" + analysis_name + "/sub-DEV*/",
    dropbox_datapath=dropbox_datapath
)

# betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)

# for contrast_name in ['CS>CG','CG>CS','CS>FS','FS>CS']:
#     contrast_colname = 'contrast_' + contrast_name + '_fname'
#     print(contrast_name)
#     if contrast_colname in betas_with_contrasts.columns:
#         for i, r in betas_with_contrasts.iterrows():
#             if pd.isnull(r[contrast_colname]) is False:
#                 tmap_filepath = r.loc['spm_l2_path'] + r.loc[contrast_colname]
#                 print("'" + tmap_filepath + ",1'")
#     else:
#         print('contrast ' + contrast_name + ' not found.')



# iterate_over_l1_images_and_run_l2_scripts(
#     beta_name_list, betas_with_paths, analysis_name, sst_level_2_path, template_filepath, spm_path,
#     col_function=lambda img_name: "beta_" + img_name + "_fname"
# )



betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)
#betas_with_paths = get_beta_fnames_for_beta_dirs(train_betas_with_data)


print(betas_with_contrasts.columns)
contrast_name_list = ['CS','CG','FS','CS>CG','CG>CS','CS>FS','FS>CS',
'CS(W2-W1)',
'CG(W2-W1)',
'FS(W2-W1)',
'CS(W1-W2)',
'CG(W1-W2)',
'FS(W1-W2)',
'CS>CG(W2-W1)',
'CG>CS(W2-W1)',
'CS>FS(W2-W1)',
'FS>CS(W2-W1)'
]

iterate_over_l1_images_and_run_l2_scripts(
    contrast_name_list, betas_with_contrasts, analysis_name, sst_level_2_path, template_filepath, spm_path,
    col_function=lambda img_name: "contrast_" + img_name + "_fname",    execute_l2_script=True
)



#print(betas_with_paths.columns)

# beta_name_list = [
#     'CorrectGo',
#     'CorrectStop',
#     'FailedStop',
#     'Cue',
#     'FailedGo'
#     ]

# iterate_over_l1_images_and_run_l2_scripts(
#     beta_name_list, betas_with_paths, analysis_name, sst_level_2_path, template_filepath, spm_path,
#     col_function=lambda img_name: "beta_" + img_name + "_fname"
# )

