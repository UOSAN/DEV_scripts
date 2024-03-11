import glob
import pandas as pd

from os.path import basename
import pickle

from level2.level2_utils import *
from level2.level2_roi_extraction import level2_roi_extractor# load_rois, get_roi_data_for_beta
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
## SST, conditions
#filter the mask_label in mask_df, using regex, to only use stiraum, finger movements, motor control, and response inbhitioin
sst_roi_df = roi_df.loc[roi_df['mask_label'].str.contains('striatum|finger|motor|response inhibition')]

train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = config['nonbids_data_path'] + "fMRI/fx/models/SST/wave1/conditions/sub-DEV*/",
    nonbids_data_path = config['nonbids_data_path'],
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = config['dev_scripts_path'] + "/fMRI/ml",
    dropbox_datapath=config['dropbox_data_dir'],
    exclude_test_subjs=False
)
train_betas_with_data['wave']=1

#we're not interestd in getting contrasts; comment this out.
#betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)
betas_with_paths = get_beta_fnames_for_beta_dirs(train_betas_with_data)

beta_name_list = [
    'CorrectGo',
    'CorrectStop',
    'FailedStop',
    #'Cue',
    #'FailedGo'
    ]

level2_extractor = level2_roi_extractor()
#get the ROI data
roi_data_sst_conditions = level2_extractor.get_roi_data_for_l2_betas(betas_with_paths, beta_name_list, sst_roi_df)

###################################
## SST, posterror conditions

train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = config['nonbids_data_path'] + "fMRI/fx/models/SST/wave1/posterror_conditions/sub-DEV*/",
    nonbids_data_path = config['nonbids_data_path'],
    #ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = config['dev_scripts_path'] + "/fMRI/ml",
    dropbox_datapath=config['dropbox_data_dir'],
    exclude_test_subjs=False
)
train_betas_with_data['wave']=1

#we're not interestd in getting contrasts; comment this out.
#betas_with_contrasts = get_contrasts_for_betas(train_betas_with_data)
betas_with_paths = get_beta_fnames_for_beta_dirs(train_betas_with_data)

beta_name_list = ['CorrectGoFollowingFailedStop']

#get the ROI data
roi_data_sst_posterror_conditions = get_roi_data_for_l2_betas(betas_with_paths, beta_name_list, sst_roi_df)

roi_data_sst=pd.concat([rddf.reset_index(inplace=False, drop=True) for rddf in [roi_data_sst_conditions, roi_data_sst_posterror_conditions]], axis=0)

roi_data_sst.to_csv(config['dropbox_data_dir'] + '/subject_sst_avg_roi_data_raw.csv')


#raise NotImplementedError("the code after this line hasn't been updated from the notebook yet.")



# ###################################
# ## COMBINE ALL

# #combine all the dataframes
# roi_data_all = pd.concat([rddf.reset_index(inplace=False,drop=True) for rddf in [roi_data_sst, roi_data_wtp, roi_data_roc]], axis=1)

# #save the data
# roi_data_all.to_csv(config['dropbox_data_dir'] + '/subject_avg_roi_data_raw.csv')