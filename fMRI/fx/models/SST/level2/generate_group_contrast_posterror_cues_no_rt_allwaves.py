import pandas as pd
import os
from glob import glob
import numpy as np
from level2_utils import get_data_for_confirmed_train_subjs, read_yaml_for_host
from level2_utils import *
import sys
sys.path.append('/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/analyses/intervention_moderation/')
from dev_interaction_util import load_groups_from_mastersheet
#beta_paths = glob("/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/beta_0002.nii")


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

spm_path = config_data['spm_path']

analysis_name = 'posterror_cues_no_rt'

output_name = analysis_name + '_groups'

groups_by_name = load_groups_from_mastersheet(dropbox_datapath + 'DEV Participant Mastersheet_copy.xlsx')

group_codes = pd.concat([groups_by_name.dev_id, pd.get_dummies(groups_by_name.intervention_group)], axis=1)
train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = nonbids_data_path + "fMRI/fx/models/SST/all_waves/" + analysis_name + "/sub-DEV*/",
    nonbids_data_path = nonbids_data_path,
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path,
    dropbox_datapath=dropbox_datapath,
    exclude_test_subjs=False
)

train_betas_with_data_w_groups = train_betas_with_data.merge(group_codes, left_on='SID', right_on='dev_id', how='inner')

betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data_w_groups)
#betas_with_paths = get_beta_fnames_for_beta_dirs(train_betas_with_data)


print(betas_with_contrasts.columns)
contrast_name_list = [
    # 'CueFollowing(CS>FS)',
    # 'CueFollowing(FS>CS)',
    # 'CorrectGoFollowing(CS>FS)',
    # 'CorrectGoFollowing(FS>CS)',
    #only W2<>W1 contrasts are meaningful;
    #what would be the point of looking at group contrasts at just wave 1 or just wave 2?
    'CueFollowingCorrectStop(W2-W1)',
    'CueFollowingCorrectStop(W1-W2)',
    'CueFollowingFailedStop(W2-W1)',
    'CueFollowingFailedStop(W1-W2)'
    #we can't contrast CG and CS because
    #we haven't prepared t-maps properly
    #considering that some cue items will be missing and the betas won't be in the same order
    # ,'CorrectStopPrecedingCorrectGo',
    #    'FailedStopPrecedingCorrectGo',
    #    'OtherCue', 'OtherCorrectGo',
    #    'OtherCorrectStop', 'OtherFailedStop',
    #    'CueFollowing(CS>FS)',
    #    'CueFollowing(FS>CS)',
    #    'CorrectGoFollowing(CS>FS)',
    #    'CorrectGoFollowing(FS>CS)',



    #    'CorrectGoFollowingCorrectStop(W2-W1)',
    #    'CorrectGoFollowingCorrectStop(W1-W2)',
    #    'CorrectGoFollowingFailedStop(W2-W1)',
    #    'CorrectGoFollowingFailedStop(W1-W2)',
    #    'CorrectStopPrecedingCorrectGo(W2-W1)',
    #    'CorrectStopPrecedingCorrectGo(W1-W2)',
    #    'FailedStopPrecedingCorrectGo(W2-W1)',
    #    'FailedStopPrecedingCorrectGo(W1-W2)'
]


iterate_over_l1_images_and_run_l2_scripts_w_confounds(
    contrast_name_list, betas_with_contrasts, output_name, sst_level_2_path, config_data['template_mlr_main'], spm_path,
    col_function=lambda img_name: "contrast_" + img_name + "_fname",
    confounders=['willamette','umpqua','mckenzie'],
    confounder_contrasts = ['umpqua>willamette','mckenzie>willamette','willamette>umpqua','willamette>mckenzie', 'umpqua>mckenzie','mckenzie>umpqua'],
    confounder_template_path = config_data['template_mlr_confounder_no_centering'],
    consess_template_path=config_data['template_mlr_consess'],
    conspec_template_path=config_data['template_mlr_conspec'],
    include_base_contrast = False,
    execute_l2_script=True
)


# to do:
#  - new templates DONE?
#  - omit main effect
#  - add group comparisons to contrast list [re-write the code in run-time, it'll be much easier] (these are the 'conspecs' only, not consess)
#  - figure out how to handle the no centering setting (other designs will need centering)
