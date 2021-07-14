'''
This script is to generate whole brain connectivity with pariwise parcial correlation for each acq
'''

import os
import argparse
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core import base
import seaborn as sns
import pingouin as pg
from nilearn.image import load_img
from nltools.data import Brain_Data, Design_Matrix, Adjacency
from nltools.mask import expand_mask, roi_to_brain
from nltools.stats import zscore, fdr, one_sample_permutation
from nltools.file_reader import onsets_to_dm
from nltools.plotting import component_viewer
from scipy.stats import binom, ttest_1samp
from sklearn.metrics import pairwise_distances
from copy import deepcopy
import networkx as nx
from nilearn.plotting import plot_stat_map, view_img_on_surf
from bids import BIDSLayout, BIDSValidator
import nibabel as nib

def extractData(base_dir, sub_id, acq_id):
    '''
    (str, str) -> Brain_Data
    This function is used to extract data from a specifc baseline acq (acq_id) of subject (sub_id) and concatenate them together. 
    '''
    # set directory & file names
    data_dir = os.path.join(base_dir, 'bids_data','rs_postfmriprep', f'sub-{sub_id}')
    acq_filename = f'sub-{sub_id}_ses-wave1_task-rest_acq-{acq_id}_bold_space-MNI152NLin2009cAsym_preproc.nii.gz'
    # extract data from each acq
    acq_data = Brain_Data(load_img(os.path.join(data_dir, acq_filename)))

    return acq_data

def load_covariates(base_dir, sub_id, acq_id):
    '''
    (str) -> DataFrame
    This function load the covariates tsv files of the given acq(acq_id). 
    '''
    cov_dir = os.path.join(base_dir, 'bids_data', 'rs_derivatives','fmriprep', f'sub-{sub_id}', 'ses-wave1', 'func')
    cov_fileName = f'sub-{sub_id}_ses-wave1_task-rest_acq-{acq_id}_bold_confounds.tsv'

    covariates = pd.read_csv(os.path.join(cov_dir, cov_fileName), sep = '\t')

    return covariates

def make_motion_covariates(covariates, tr):
    '''
    (DataFrame) -> DataFrame

    This function extract and process motion regressors. This function will be called by make_design_matrix
    '''
    mc = covariates[['X','Y','Z','RotX', 'RotY', 'RotZ']]
    z_mc = zscore(mc)
    all_mc = pd.concat([z_mc, z_mc**2, z_mc.diff(), z_mc.diff()**2], axis=1)
    all_mc.fillna(value=0, inplace=True)
    return Design_Matrix(all_mc, sampling_freq=1/tr)

def make_design_matrix(data, covariates, tr):
    '''
    (Brain_Data, Data_Frame, float) -> 
    This function will make a design matrix with the seed regressor and nusiance regressor including, motion, CSF, whitematter & spikes
    '''

    other_cov = covariates[['CSF', 'WhiteMatter']].apply(zscore)
    mc = make_motion_covariates(covariates, tr)
    spikes = data.find_spikes(global_spike_cutoff=3, diff_spike_cutoff=3)
    dm = Design_Matrix(pd.concat([other_cov, mc, spikes.drop(labels='TR', axis=1)], axis=1), sampling_freq=1/tr)
    dm = dm.add_poly(order=2, include_lower=True)

    return dm

# set subject ID from the imput 
parser = argparse.ArgumentParser(description='subject level rs connectivity analysis')
parser.add_argument(
    '--sub-id',
    required=True,
    action='store',
    help='subject id')
args = parser.parse_args()

# set dataset parameter
base_dir = '/projects/sanlab/shared/DEV/'
sub_id = args.sub_id
tr = 0.78

# load the parcellation mask
mask_dir = os.path.join(base_dir, 'DEV_scripts', 'rsfMRI', 'baseline_analysis')
mask = Brain_Data(os.path.join(mask_dir, 'BN_Atlas_246_2mm.nii.gz'))
mask_x = expand_mask(mask)

# loop through both acquisition
for acq in range(1,3):
    # load the concatenated data
    data = extractData(base_dir, sub_id, acq)
    # load the concatenated covariates
    covariates = load_covariates(base_dir, sub_id, acq)
    # make a design matrix
    dm = make_design_matrix(data, covariates, tr)
    data.X = dm
    # denoise the data
    stats = data.regress()
    data_denoised = stats['residual']
    # extract time series of each roi
    rois_data = data_denoised.extract_roi(mask=mask)
    # compute pair-wise partial correlation
    rois_df = pd.DataFrame(rois_data.T)
    roi_pcorr = rois_df.pcorr().to_numpy()
    # write the partial correlation to file
    fileName = sub_id + '_' + str(acq) + '_' + 'pcorr.csv'
    output_dir = os.path.join('/projects/sanlab/shared/DEV/DEV_scripts/rsfMRI/607_project/', 'subject_pcorr', fileName)
    pcorr_df = pd.DataFrame(roi_pcorr)
    pcorr_df.to_csv(output_dir, index=False, header=False)