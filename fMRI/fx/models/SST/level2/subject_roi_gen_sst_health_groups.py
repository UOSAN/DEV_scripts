import glob
import pandas as pd

from os.path import basename
import pickle
import sys

#print paths available to import from
#get the parent directory of the current directory
parent_dir = '/'.join(sys.path[0].split('/')[0:-1])
sys.path.append(parent_dir)
print(sys.path)


from direct_regression.get_all_series import get_beta_img, get_roi_data, get_moment_trial_type_revealed, get_behavioral_data_with_moment_trial_type_revealed, mask_3d_subject_image
from direct_regression.get_all_series import get_all_subj_df
from direct_regression.fmri_utils import *

from level2_utils import *
from level2_roi_extraction import level2_roi_extractor# load_rois, get_roi_data_for_beta
from level2_roi_extraction import get_roi_data_for_l2_betas, get_roi_data_for_multirun_l2_betas
#import modules from files in a parallel directory "direct_regression"


sys.path.append('/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/analyses/intervention_moderation/')
#sys.path.append('/Users/bensmith/Documents/code/DEV_scripts/analyses/intervention_moderation/')
from dev_interaction_util import load_groups_from_mastersheet

sys.path.append('../../')
from models.modeling_utils import get_sst_subj_folder_paths_for_subjs_w_two_sessions






config = load_config("direct_regression/config.yml")
analysis_name = 'health_conditions'

output_name = analysis_name + '_groups'


#get the masks
mask_locations = [
    #config['mask_location'] + 'aim3/masks/neurosynth/',
    config['mask_location'] + 'aim3/',
    config['mask_location'] + 'striatum/',#,
    config['mask_location'] + 'value/value_association-test_z_FDR_0.01_t9',
    config['mask_location'] + 'value/value_association_frontal_medial_cortex_t5',
    config['mask_location'] + 'value/anatomical_based/fmc_paracing_t25_value_t5',
    config['mask_location'] + 'value/anatomical_based/fmc_paracingulate_t50',
    config['mask_location'] + 'response_inhibition_related/response inhibition_association-test_z_FDR_0.01_t5'
]

signature_locations = [
    config['mask_location'] + 'sst_functional/'
]

roi_df = get_mask_df_from_mask_locations(mask_locations)
signature_df = get_mask_df_from_mask_locations(signature_locations)
roi_df['image_type'] = 'mask'
signature_df['image_type'] = 'signature'

#combine the two dfs
roi_df = pd.concat([signature_df, roi_df])
#get the list of raw nii files
glob_path = config['fmriprep_dir'] + config['nii_raw_path']
dropbox_datapath = config['dropbox_data_dir']

###################################
## SST, health conditions
#filter the mask_label in mask_df, using regex, to only use stiraum, finger movements, motor control, and response inbhitioin
#sst_roi_df = roi_df.loc[roi_df['mask_label'].str.contains('striatum|finger|motor|response inhibition')]

# train_betas_with_data = get_data_for_confirmed_train_subjs(
#     beta_glob = config['nonbids_data_path'] + "fMRI/fx/models/SST/wave1/conditions/sub-DEV*/",
#     nonbids_data_path = config['nonbids_data_path'],
#     #ml_data_folderpath = ml_data_folderpath,
#     ml_scripting_path = config['dev_scripts_path'] + "/fMRI/ml",
#     dropbox_datapath=config['dropbox_data_dir'],
#     exclude_test_subjs=False
# )[0:20]

groups_by_name = load_groups_from_mastersheet(dropbox_datapath + 'DEV Participant Mastersheet_copy.xlsx')

group_codes = pd.concat([groups_by_name.dev_id, pd.get_dummies(groups_by_name.intervention_group)], axis=1)



train_betas_with_data = get_sst_subj_folder_paths_for_subjs_w_two_sessions(
    beta_glob = config['nonbids_data_path'] + "fMRI/fx/models/SST/all_waves/health_conditions/sub-DEV*/",
    dropbox_datapath=config['dropbox_data_dir'],
    automotion_datapath = config['automotion_output_path']
)[0:20]
#get unique rows for a subset of the cols


train_betas_with_data_w_groups = train_betas_with_data.merge(group_codes, left_on='SID', right_on='dev_id', how='inner')

betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data_w_groups,use_tmaps=False)


#train_betas_with_data['wave']=1

#we're not interestd in getting contrasts; comment this out.
#betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)
# betas_with_paths = get_beta_fnames_for_beta_dirs(train_betas_with_data)

contrast_name_list = [
    'Stop(Healthy>Unhealthy)(W1-W2)',
    'Stop'
    #'Cue',
    #'FailedGo'
    ]

#get the ROI data
l2_roi_extractor = level2_roi_extractor()
l2_roi_extractor.image_standardize=True
l2_roi_extractor.load_all_images_simultaneously=True
#l2_roi_extractor = level2_roi_extractor(center_data=True, scale_data=True)

#one of:
#get_roi_data_across_all_betas(self,beta_list: pd.DataFrame, condition,col_function, raw_roi_list, roi_df)
#get_roi_data_for_roi_col(self,beta_list, condition,col_function, raw_roi_list, roi_df):
#get_roi_data_for_l2(self, beta_list,condition_list,roi_df,col_function):
#get_roi_data_for_l2_betas(self, beta_list, condition_list,roi_df):

roi_data_sst_health = l2_roi_extractor.get_roi_data_for_l2_contrasts(betas_with_contrasts[0:20], contrast_name_list, roi_df)


#roi_data_sst_health.to_csv(config['dropbox_data_dir'] + '/subject_sst_health_avg_roi_data_raw.csv')
roi_data_sst_health.to_csv(config['dropbox_data_dir'] + '/subject_sst_group_health_avg_roi_data_raw_zscored2.csv')


#raise NotImplementedError("the code after this line hasn't been updated from the notebook yet.")



# ###################################
# ## COMBINE ALL

# #combine all the dataframes
# roi_data_all = pd.concat([rddf.reset_index(inplace=False,drop=True) for rddf in [roi_data_sst, roi_data_wtp, roi_data_roc]], axis=1)

# #save the data
# roi_data_all.to_csv(config['dropbox_data_dir'] + '/subject_avg_roi_data_raw.csv')