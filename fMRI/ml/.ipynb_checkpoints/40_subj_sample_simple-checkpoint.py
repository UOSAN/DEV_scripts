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
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut,LeaveOneGroupOut
import os, warnings



#custom thing I have set in my jupyter notebook task.
cpus_available = int(os.getenv('CPUS_PER_TASK'))
print(cpus_available)

pd.set_option('display.max_rows', 99)


test_train_set = pd.read_csv("../data/train_test_markers_20210601T183243.csv")

with open('../data/Brain_Data_2sns_40subs.pkl', 'rb') as pkl_file:
    Brain_Data_allsubs = pickle.load(pkl_file)
    
dev_wtp_io_utils.check_BD_against_test_train_set(Brain_Data_allsubs,test_train_set)

#################################################
#######PRE-PROCESS

Brain_Data_allsubs.Y = Brain_Data_allsubs.X.response.copy()
print(Brain_Data_allsubs.Y.value_counts())
Brain_Data_allsubs.Y[Brain_Data_allsubs.Y=='NULL']=None
print(Brain_Data_allsubs.Y.value_counts())

import sys
for name, size in sorted(((name, sys.getsizeof(value)) for name, value in locals().items()),
                         key= lambda x: -x[1])[:60]:
    print(name + ': ' + str(size))
print(Brain_Data_allsubs.Y.isnull().value_counts())
Brain_Data_allsubs_nn = Brain_Data_allsubs[Brain_Data_allsubs.Y.isnull()==False]
print(len(Brain_Data_allsubs_nn))
print(len(Brain_Data_allsubs))


all_subs_nn_nifti = Brain_Data_allsubs_nn.to_nifti()
all_subs_nn_nifti_Y = Brain_Data_allsubs_nn.Y
all_subs_nn_nifti_groups = Brain_Data_allsubs_nn.X.subject
all_subs_nn_nifti_groups


all_subs_nn_nifti_metadata = Brain_Data_allsubs_nn.X


#################################################
#######GET SUB-SET


del Brain_Data_allsubs
#del Brain_Data_allsubs_grouped
gc.collect()

from nilearn.decoding import DecoderRegressor
dRegressor = DecoderRegressor(estimator = 'ridge_regressor', standardize= True,scoring="r2")


asizeof_fmt(Brain_Data_allsubs_nn)

asizeof_fmt(all_subs_nn_nifti)

print("cleaning")
train_y=all_subs_nn_nifti_Y
train_X = nil.image.clean_img(all_subs_nn_nifti,detrend=False,standardize=True)
train_groups = all_subs_nn_nifti_groups

del Brain_Data_allsubs_nn
gc.collect()

first_subs_nifti_metadata = all_subs_nn_nifti_metadata

cv_outer = LeaveOneGroupOut()

print("finished preprocessing")


regressor = DecoderRegressor(standardize= True,cv=LeaveOneGroupOut(),scoring="r2",
                                  n_jobs=cpus_available-1,verbose=1)

print("created regressor")

#We have put all the CV into the regressor itself. So we will not bother with any further cross-validation.

regressor.fit(y=train_y,X=train_X,groups=train_groups)

print("finished fitting")



import pickle
with open("../data/cv_train_test_40subjs_loocv_simple.pkl", 'wb') as handle:
    pickle.dump(regressor,handle)
    
    