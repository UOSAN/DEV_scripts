import glob
import pandas as pd
import re
import nilearn as nil
from nilearn import *
from nilearn import image
from os.path import basename
import numpy as np
import yaml
from yaml.loader import SafeLoader
from socket import gethostname

from get_all_series import get_roi_data, get_moment_trial_type_revealed, get_behavioral_data_with_moment_trial_type_revealed
from get_all_series import get_all_subj_df

print(gethostname())
# Open the file and load the file
with open('config.yml') as f:
    all_yaml = yaml.load(f, Loader=SafeLoader)
    if gethostname() in all_yaml.keys():
        config = all_yaml[gethostname()]
    else:
        config = all_yaml['default']
        
print(config)
        
        
# #need to replace these with references to the config yml
# dropbox_data_dir = '/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/analysis_files/data/'
# fmriprep_dir = '/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep/'
# nii_raw_path = 'sub-DEV*/ses-wave1/func/s6_sub-DEV*_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii'
# mask_location = '/Users/benjaminsmith/Google Drive/oregon/data/DEV/brainmaps/striatum/'
dropbox_data_dir = config['dropbox_data_dir']
fmriprep_dir = config['fmriprep_dir']
nii_raw_path = config['nii_raw_path']
mask_location = config['mask_location'] + 'striatum/'


sst_all_behavioral_data = pd.read_csv(dropbox_data_dir + "/sst_behavioral_data_all.csv")



sst_all_behavioral_data = get_behavioral_data_with_moment_trial_type_revealed(sst_all_behavioral_data)

sst_all_behavioral_data['class_type_reveal_onset'] = sst_all_behavioral_data.class_type_reveal + sst_all_behavioral_data.onset
sst_all_behavioral_data.loc[sst_all_behavioral_data.go_no_go_condition_label=='Cue','class_type_reveal_onset']=None

sst_all_behavioral_data.to_csv(dropbox_data_dir + "/sst_behavioral_data_all_w_class_type_reveal_onset.csv")

