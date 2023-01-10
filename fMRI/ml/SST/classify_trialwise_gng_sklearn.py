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



def main(bd_filename, response_transform_function = trialtype_resp_trans_func):


    brain_data_filepath = ml_data_folderpath + bd_filename

    warnings.warn("not sure if this file holds up--it was created in 2021; need to see if it's still valid")
    train_test_markers_filepath = ml_data_folderpath + "/train_test_markers_20230102T164214.csv"



    all_subjects = load_and_preprocess_Brain_Data(
        brain_data_filepath,
        train_test_markers_filepath,
        #subjs_to_use = None,
        response_transform_func = response_transform_function
        #clean=None
        )
    #filter out any subjects that don't have all the outcome groups
    # outcome_groups = pd.DataFrame(
    #     {'outcomes':all_subjects.Y,'subjects':all_subjects.X['subject']}
    #     ).value_counts()
    # #identify any subjects with missing outcome groups
    # missing_outcome_groups = outcome_groups[outcome_groups==0].index.get_level_values('subject').unique()
    # outcome_groups

    #remove any features that are all NaN
    not_na_cols=np.isnan(all_subjects.data).all(axis=0)==False
    cleaned_data=all_subjects.data[:,not_na_cols]
    all_subjects.data=cleaned_data

    #find out how many nan features there are in each sample
    nan_features_per_sample = np.isnan(all_subjects.data).sum(axis=1)
    #find out which subject each of those samples are associated with
    nan_features_per_sample_subjs = all_subjects.X['subject'].iloc[nan_features_per_sample>0]
    subjects_with_nan_features = nan_features_per_sample_subjs.unique()
    print("there are " + str(len(subjects_with_nan_features)) + " subjects with nan features. all the subject data will be removed from the dataset",end="")
    #remove those subjects from the dataset
    all_subjects = all_subjects[~all_subjects.X['subject'].isin(subjects_with_nan_features)]
    #okay, so it's just one subject. so we can remove them, and move on!
    print("...removed.")




    #convert the y array to an integer array representing the string values of the y array
    all_subjects_y_cat = all_subjects.Y.astype('category')
    all_subjects_y_int=all_subjects_y_cat.cat.codes

    #mask_nifti = nib.load(ml_data_folderpath + '/prefrontal_cortex.nii.gz')

    num_subjs = len(all_subjects.X['subject'].unique())
    if num_subjs < len(all_subjects.X['subject'].unique()):
        #select subjs
        subjs = all_subjects.X['subject'].unique()
        subjs.sort()
        selected_sub_ids=subjs[0:num_subjs]
        selected_rows = all_subjects.X['subject'].isin(selected_sub_ids)
        selected_subjs = all_subjects[selected_rows]
        selected_subjs_y_int = all_subjects_y_int[selected_rows]
    else:
        print("using all subjects")
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

    cv_result = sklearn_nested_cross_validate(
        selected_subjs.data,
        np.array(selected_subjs_y_int),
        estimators_with_fs,
        groups=np.array(selected_subjs.X['subject']))

    
            
    print(pd.Series(cv_result['y_predict_final']).value_counts())
    print(roc_auc_score(selected_subjs_y_int,cv_result['y_predict_final']))

    return(cv_result)

        
if __name__ == "__main__":
    main(bd_filename = '/SST/Brain_Data_betaseries_nos_6subs_correct_cond_pfc.pkl')