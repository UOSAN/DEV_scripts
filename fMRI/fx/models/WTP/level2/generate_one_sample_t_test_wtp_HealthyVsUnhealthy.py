import pandas as pd
import os
from glob import glob
import numpy as np
import sys
sys.path.append("fMRI/fx/models/")
from modeling_utils import load_config
config_data = load_config("fMRI/fx/models/WTP/level2/l2_config.yml")
import yaml
sys.path.append(config_data['sst_level_2_analysis_path'])
from level2_utils import *
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")



#beta_df['spm_l2_path_description'] =beta_df.beta_filepath
#paths
nonbids_data_path = config_data['nonbids_data_path']
dropbox_data_path = config_data['dropbox_datapath']
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path = config_data['dev_scripts_path']
ml_scripting_path = dev_scripts_path + "/fMRI/ml"

wtp_level1_path = nonbids_data_path + "fMRI/fx/models/WTP/all_waves/conditions/sub-DEV*/"
wtp_level2_path = config_data['wtp_level2_path']
template_filepath = config_data['spm_l2_script_template_filepath']
spm_path = config_data['spm_path']

analysis_name = 'prepostWTP'
train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = wtp_level1_path,
    nonbids_data_path = nonbids_data_path,
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path,
    dropbox_datapath=dropbox_data_path,
    exclude_test_subjs=False,
    task="WTP"
)


betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)

contrast_name_list = ['HealthyLiked(T2>T1)','UnhealthyLiked(T2>T1)','HealthyDisliked(T2>T1)','UnhealthyDisliked(T2>T1)', 'HealthyVSUnhealthy', 'UnealthyVSHealthy', 'HealthyLikedVsUnhealthyLiked', 'UnhealthyLikedVsHealthyLiked'], 
#contrast_name_list = ['HealthyLiked(T2>T1)','UnhealthyLiked(T2>T1)','HealthyDisliked(T2>T1)','UnhealthyDisliked(T2>T1)', 'HealthyLiked(T2<T1)','UnhealthyLiked(T2<T1)','HealthyDisliked(T2<T1)','UnhealthyDisliked(T2<T1)', 'HealthyVSUnhealthy', 'UnealthyVSHealthy', 'HealthyLikedVsUnhealthyLiked', 'UnhealthyLikedVsHealthyLiked'] 
# for contrast_name in ['HealthyLiked(T2>T1)','UnhealthyLiked(T2>T1)','HealthyDisliked(T2>T1)','UnhealthyDisliked(T2>T1)']:
#     contrast_colname = 'contrast_' + contrast_name + '_fname'
#     print(contrast_name)
#     if contrast_colname in betas_with_contrasts.columns:
#         for i, r in betas_with_contrasts.iterrows():
#             if pd.isnull(r[contrast_colname]) is False:
#                 tmap_filepath = r.loc['spm_l2_path'] + r.loc[contrast_colname]
#                 print("'" + tmap_filepath + ",1'")
#     else:
#         print('contrast ' + contrast_name + ' not found.')


# #[print(s) for s in train_betas_with_data.spm_l2_path_description]

iterate_over_l1_images_and_run_l2_scripts(
    contrast_name_list, 
    l1_images_with_paths = betas_with_contrasts, 
    analysis_name = analysis_name, 
    sst_level_2_path = wtp_level2_path, 
    template_filepath = template_filepath, 
    spm_path = spm_path,
    col_function=lambda img_name: 'contrast_' + img_name + "_fname"
    )
