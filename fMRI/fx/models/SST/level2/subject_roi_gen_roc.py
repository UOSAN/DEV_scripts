import glob
import pandas as pd

from os.path import basename
import pickle

from level2.level2_utils import *
from level2.level2_roi_extraction import load_rois, get_roi_data_for_beta
from level2.level2_roi_extraction import get_roi_data_for_l2_betas, get_roi_data_for_multirun_l2_betas
#import modules from files in a parallel directory "direct_regression"


from direct_regression.get_all_series import get_beta_img, get_roi_data, get_moment_trial_type_revealed, get_behavioral_data_with_moment_trial_type_revealed, mask_3d_subject_image
from direct_regression.get_all_series import get_all_subj_df
from direct_regression.fmri_utils import *



config = load_config("direct_regression/config.yml")
analysis_name = 'conditions'


#get the masks
mask_locations = [
    config['mask_location'] + 'aim3/masks/neurosynth/',
    config['mask_location'] + 'aim3/masks/'
]

signature_locations = [
    config['mask_location'] + 'aim3/signatures/'
]

roi_df = get_mask_df_from_mask_locations(mask_locations)
signature_df = get_mask_df_from_mask_locations(signature_locations)
roi_df['image_type'] = 'mask'
signature_df['image_type'] = 'signature'

#combine the two dfs
roi_df = pd.concat([roi_df, signature_df])
#get the list of raw nii files
glob_path = config['fmriprep_dir'] + config['nii_raw_path']


###################################
## ROC
roc_mask_df = roi_df.loc[roi_df['mask_label'].str.contains('reappraisal|abstract|attention|striatum|craving|regulation')]


train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = config['nonbids_data_path'] + "fMRI/fx/models/ROC/wave1/conditions/sub-DEV*/",
    nonbids_data_path = config['nonbids_data_path'],
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = config['dev_scripts_path'] + "/fMRI/ml",
    dropbox_datapath=config['dropbox_data_dir'],
    exclude_test_subjs=False,
    task='ROC'
).copy()
train_betas_with_data['wave']=1



#we're not interestd in getting contrasts; comment this out.
#betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)
betas_with_paths = get_beta_fname_list_for_beta_dirs(train_betas_with_data)



#from level2.level2_roi_extraction import get_roi_data_for_l2_betas, get_roi_data_for_multirun_l2_betas

beta_name_list = [
    'lookCrave',
    'reappraiseCrave'
    ]

#get the ROI data
roi_data_roc = get_roi_data_for_multirun_l2_betas(betas_with_paths, condition_list = beta_name_list, mask_df = roc_mask_df)

roi_data_roc.to_csv(config['dropbox_data_dir'] + '/subject_roc_avg_roi_data_raw.csv')

