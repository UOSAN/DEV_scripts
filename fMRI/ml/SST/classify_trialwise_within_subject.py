import socket
import yaml
hostname=socket.gethostname()
hostname='zzz'

import sys
import os
import pandas as pd
import numpy as np



sys.path.append(os.path.abspath("../../ml/"))
from apply_loocv_and_save import load_and_preprocess, load_and_preprocess_Brain_Data
from dev_utils import read_yaml_for_host, get_2DX_from_4DX
import warnings

if os.path.isfile("sst_config.yml"):
    config_data = read_yaml_for_host("sst_config.yml")
else:
    config_data = read_yaml_for_host("SST/sst_config.yml")

from sklearn.pipeline import Pipeline
from sklearn.svm import SVC, LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import f_classif, SequentialFeatureSelector, SelectKBest
from sklearn.feature_selection import SelectPercentile, VarianceThreshold
from sklearn.linear_model import LogisticRegression, RidgeClassifierCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut, LeaveOneGroupOut
from sklearn import decomposition
import multiprocessing
import math
import nibabel as nib
import nilearn as nl
from nilearn.decoding import DecoderRegressor,Decoder

cpus_available = multiprocessing.cpu_count()

cpus_to_use = min(cpus_available-1,math.floor(0.9*cpus_available))
print(cpus_to_use)


from dev_wtp_io_utils import cv_train_test_sets, asizeof_fmt
from dev_utils import sklearn_nested_cross_validate

nonbids_data_path = config_data['nonbids_data_path']
ml_data_folderpath = nonbids_data_path + "fMRI/ml"




def trialtype_resp_trans_func(X):
    return(X.trial_type)



def main(bd_filename):


    brain_data_filepath = ml_data_folderpath + bd_filename

    warnings.warn("not sure if this file holds up--it was created in 2021; need to see if it's still valid")
    train_test_markers_filepath = ml_data_folderpath + "/train_test_markers_20230102T164214.csv"



    all_subjects = load_and_preprocess_Brain_Data(
        brain_data_filepath,
        train_test_markers_filepath,
        #subjs_to_use = None,
        response_transform_func = trialtype_resp_trans_func
        #clean=None
        )

    #convert the y array to an integer array representing the string values of the y array
    all_subjects_y_cat = all_subjects.Y.astype('category')
    all_subjects_y_int=all_subjects_y_cat.cat.codes

    mask_nifti = nib.load(ml_data_folderpath + '/prefrontal_cortex.nii.gz')

    num_subjs = 6
    if num_subjs < len(all_subjects.X['subject'].unique()):
        #select subjs
        subjs = all_subjects.X['subject'].unique()
        subjs.sort()
        selected_sub_ids=subjs[0:num_subjs]
        selected_rows = all_subjects.X['subject'].isin(selected_sub_ids)
        selected_subjs = all_subjects[selected_rows]
        selected_subjs_y_int = all_subjects_y_int[selected_rows]
    else:
        selected_subjs = all_subjects
        selected_subjs_y_int = all_subjects_y_int

    estimators = [
        LogisticRegression(penalty='l2',solver='liblinear',class_weight='balanced'),
        RidgeClassifierCV(class_weight='balanced')
    ]
    estimators_with_fs = []
    #now wrap the estimators in a pipeline that does feature selection
    for estimator in estimators:
        estimator_with_fs = Pipeline([
            ('clean',VarianceThreshold(threshold=0)),
            ('select', SelectKBest(f_classif, k=200)),
            ('estimator', estimator)])
        estimators_with_fs.append(estimator_with_fs)

    for subj in np.unique(selected_subjs.X['subject']):
        #do classification one subject at a time.
        this_subj_samples = selected_subjs.X['subject']==subj
        print(subj)

        #create some pseudogroups, ensuring that each group has some of each outcome type
        this_subj_y = selected_subjs_y_int[this_subj_samples]
        group_size = this_subj_y.value_counts().min()
        #now assign every item in each sample to a number between 1 and group_size
        #cumulatively number each item type in the sample
        pseudo_groups = this_subj_y.groupby(this_subj_y).cumcount() % group_size + 1


        cv_result = sklearn_nested_cross_validate(
            selected_subjs[this_subj_samples].data,
            np.array(this_subj_y),
            estimators_with_fs,
            groups=np.array(pseudo_groups))

        print(pd.Series(cv_result['y_predict_final']).value_counts())
        print(roc_auc_score(this_subj_y,cv_result['y_predict_final']))

        
if __name__ == "__main__":
    main(bd_filename = '/SST/Brain_Data_betaseries_nos_6subs_correct_cond_pfc.pkl')