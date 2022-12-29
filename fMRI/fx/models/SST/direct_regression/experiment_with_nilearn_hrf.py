import glob
import pandas as pd
import re
import nilearn as nil
from nilearn import *
from nilearn import image
from nilearn.glm.first_level import compute_regressor, spm_hrf
from os.path import basename
import numpy as np
import yaml
from yaml.loader import SafeLoader
from socket import gethostname
from scipy.signal import deconvolve
from get_all_series import get_roi_data, get_moment_trial_type_revealed, get_behavioral_data_with_moment_trial_type_revealed
from get_all_series import get_all_subj_df
#import matlibplot
import matplotlib.pyplot as plt
print('loading image')
nii_filepath = '/Users/benjaminsmith/Google Drive/oregon/data/DEV/bids_data/derivatives/fmriprep/sub-DEV293/ses-wave1/func/s6_sub-DEV293_ses-wave1_task-SST_acq-1_bold_space-MNI152NLin2009cAsym_preproc.nii'
#open a raw nii file
nii_img = image.load_img(nii_filepath)
print('cleaning image')
#apply nilearn clean image
nii_img_clean = image.clean_img(nii_img, detrend=True, standardize=True, low_pass=0.1, high_pass=0.01, t_r=2.0)
print('image cleaned')
#apply the hemodynamic response function
#nii_img_clean_hrf = compute_regressor(nii_img_clean, hrf_model = 'spm', design_matrix=None, confounds=None, n_jobs=1, minimize_memory=True, verbose=0)

tr=2.0
time_length = 32.0
#create time series with linspace
time_series = [i for i in range(0,int(time_length),int(tr))]

spm_function=spm_hrf(tr,oversampling=1,time_length=time_length,onset=0)
#plot the spm_function against time_series
plt.plot(time_series, spm_function)

activity = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] + [0]*30
time_series = [i*tr for i in range(len(activity))]
convolved_activity = np.convolve(activity, spm_function)

plt.plot(time_series, convolved_activity[0:len(time_series)])

#OK. That'll do it, but it looks crap.
#oh also--you can't convolve activity with this. you need to do the reverse convolution operation to get neural activity from bold activity using this
deconvolve(convolved_activity,spm_function)
plt.plot(deconvolve(spm_function,convolved_activity)[1])
#this recovers the SPM function, lol, not the activity