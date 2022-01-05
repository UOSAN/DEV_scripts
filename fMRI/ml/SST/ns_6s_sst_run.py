import sys
import os
import pandas as pd

sys.path.append(os.path.abspath("../../ml/"))

from apply_loocv_and_save import *
import gc
import nibabel as nib

nonbids_data_path = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/"
ml_data_folderpath = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/ml"
test_train_df = pd.read_csv(nonbids_data_path + "fMRI/ml/train_test_markers_20210601T183243.csv")

all_sst_events= pd.read_csv(ml_data_folderpath +"/SST/" + "all_sst_events.csv")


dataset_name = 'betaseries'
brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_' + dataset_name + '_6subs.pkl'

with open(brain_data_filepath, 'rb') as pkl_file:
    Brain_Data_allsubs = pickle.load(pkl_file)
    
    

def response_transform_func(X):
    return(X.trial_type)


from nilearn.decoding import DecoderRegressor, Decoder

script_path = '/gpfs/projects/sanlab/shared/DEV/DEV_scripts/fMRI/ml'
data_path = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/ml/"
# HRF 2s
dataset_name = 'betaseries'
apply_loocv_and_save(
    results_filepath=data_path + "SST/train_test_results_" + dataset_name + "_6subs.pkl",
    brain_data_filepath = data_path + 'SST/Brain_Data_' + dataset_name + '_6subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 6,
    response_transform_func = response_transform_func,
    decoderConstructor=Decoder #for classification
)
