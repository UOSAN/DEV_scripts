import pandas as pd
import numpy as np
import os
import nltools as nlt
import nilearn as nil
import nibabel as nib
import warnings
import glob
import random
import pickle
import dev_wtp_io_utils
import gc #garbage collection
from nilearn import plotting
from dev_wtp_io_utils import cv_train_test_sets, asizeof_fmt
from sklearn.model_selection import KFold,GroupKFold
import os, warnings
from nilearn.decoding import DecoderRegressor

#################################################################
#load the data

test_train_set = pd.read_csv("../data/train_test_markers_20210601T183243.csv")
with open('../data/Brain_Data_2sns_60subs.pkl', 'rb') as pkl_file:
    Brain_Data_allsubs = pickle.load(pkl_file)
    
dev_wtp_io_utils.check_BD_against_test_train_set(Brain_Data_allsubs,test_train_set)

with open('../data/Brain_Data_2sns_60subs_grouped.pkl', 'rb') as pkl_file:
    Brain_Data_allsubs_grouped = pickle.load(pkl_file)
    
dev_wtp_io_utils.check_BD_against_test_train_set(Brain_Data_allsubs_grouped,test_train_set)

print(str(datetime.datetime.now()))

#################################################################
#preprocess

Brain_Data_allsubs.Y = Brain_Data_allsubs.X.response.copy()
print(Brain_Data_allsubs.Y.value_counts())
Brain_Data_allsubs.Y[Brain_Data_allsubs.Y=='NULL']=None
print(Brain_Data_allsubs.Y.value_counts())
print(Brain_Data_allsubs.Y.isnull().value_counts())
Brain_Data_allsubs_nn = Brain_Data_allsubs[Brain_Data_allsubs.Y.isnull()==False]
print(len(Brain_Data_allsubs_nn))
print(len(Brain_Data_allsubs))


all_subs_nn_nifti = Brain_Data_allsubs_nn.to_nifti()
all_subs_nn_nifti_Y = Brain_Data_allsubs_nn.Y
all_subs_nn_nifti_groups = Brain_Data_allsubs_nn.X.subject
all_subs_nn_nifti_groups

Brain_Data_allsubs_grouped.Y = Brain_Data_allsubs_grouped.X.response.copy()
print(Brain_Data_allsubs_grouped.Y.value_counts())
all_subs_grouped_nifti = Brain_Data_allsubs_grouped.to_nifti()
all_subs_grouped_nifti_Y = Brain_Data_allsubs_grouped.Y
all_subs_grouped_nifti_groups = Brain_Data_allsubs_grouped.X.subject
all_subs_grouped_nifti_groups

#################################################################
### Get subset


print(str(datetime.datetime.now()))


del Brain_Data_allsubs
del Brain_Data_allsubs_grouped
gc.collect()

sample_subject_items = np.unique(all_subs_nn_nifti_groups)[0:30]


sample_subject_vector = [i for i, x in enumerate(all_subs_nn_nifti_groups) if x in sample_subject_items]
sample_grouped_subject_vector = [i for i, x in enumerate(all_subs_grouped_nifti_groups) if x in sample_subject_items]

first_subs_nifti = nib.funcs.concat_images([all_subs_nn_nifti.slicer[...,s] for s in sample_subject_vector])
first_subs_nifti_Y = all_subs_nn_nifti_Y[sample_subject_vector]
first_subs_nifti = nil.image.clean_img(first_subs_nifti,detrend=False,standardize=True)
first_subs_nifti_groups = all_subs_nn_nifti_groups[sample_subject_vector]

del all_subs_nn_nifti
gc.collect()

first_subs_grouped_nifti = nib.funcs.concat_images([all_subs_grouped_nifti.slicer[...,s] for s in sample_grouped_subject_vector])
first_subs_grouped_nifti_Y = all_subs_grouped_nifti_Y[sample_grouped_subject_vector]
first_subs_grouped_nifti = nil.image.clean_img(first_subs_grouped_nifti,detrend=False,standardize=True)
first_subs_grouped_nifti_groups = all_subs_grouped_nifti_groups[sample_grouped_subject_vector]

del all_subs_grouped_nifti
gc.collect()

#################################################################
###nested CV
print(str(datetime.datetime.now()))

#set up regressors to try out
cv_outer = KFold(n_splits=3)
cv_inner =  GroupKFold(3)
param_grid = {'C':[0.04,0.2,1]}


svr_reg_set = []
ridge_reg_set = []
for sp in [5,20]:
    svr_reg = DecoderRegressor(
    estimator = 'svr',
    param_grid = param_grid,
    screening_percentile = sp,
    standardize= True,cv=cv_inner, scoring="r2"
    )
    svr_reg_set = svr_reg_set + [svr_reg]
    

    ridgereg = DecoderRegressor(
        estimator = 'ridge',
        screening_percentile = sp,
        standardize= True,cv=cv_inner, scoring="r2"
    )
    ridge_reg_set = ridge_reg_set + [ridgereg]

regressors = ridge_reg_set + svr_reg_set


test_scores_different = cv_train_test_sets(
    trainset_X=first_subs_grouped_nifti,
    trainset_y=first_subs_grouped_nifti_Y,
    trainset_groups=first_subs_grouped_nifti_groups,
    testset_X=first_subs_nifti,
    testset_y=first_subs_nifti_Y,
    testset_groups=first_subs_nifti_groups,
    regressors = regressors,
    cv=cv_outer)


test_scores_same = cv_train_test_sets(
    trainset_X=first_subs_grouped_nifti,
    trainset_y=first_subs_grouped_nifti_Y,
    trainset_groups=first_subs_grouped_nifti_groups,
    regressors = regressors,
    cv=cv_outer)