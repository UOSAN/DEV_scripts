print("python initialized for apply_loocv_and_save")


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
from nilearn.decoding import Decoder
from dev_wtp_io_utils import cv_train_test_sets, asizeof_fmt
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut
import os, warnings
import pickle

cpus_available = int(os.getenv('CPUS_PER_TASK'))
#custom thing I have set in my jupyter notebook task.
print(cpus_available)
cpus_to_use = cpus_available-1


def apply_dichotomized_prediction_loocv_and_save(
    results_filepath,
    brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    subjs_to_use = None, #set this to get a subset, otherwise use all of them.
    mask=None
    ):
    #pd.set_option('display.max_rows', 99)
    test_train_set = pd.read_csv(train_test_markers_filepath)

    with open(brain_data_filepath, 'rb') as pkl_file:
        Brain_Data_allsubs = pickle.load(pkl_file)
    
    dev_wtp_io_utils.check_BD_against_test_train_set(Brain_Data_allsubs,test_train_set)

    #################################################
    #######PRE-PROCESS
    response_dichotomized = Brain_Data_allsubs.X['response'].copy()>Brain_Data_allsubs.X['response'].mean()
    Brain_Data_allsubs.Y = response_dichotomized.astype(int)
    print(Brain_Data_allsubs.Y.value_counts())
    Brain_Data_allsubs.Y[Brain_Data_allsubs.Y=='NULL']=None
    print(Brain_Data_allsubs.Y.value_counts())

#     import sys
#     for name, size in sorted(((name, sys.getsizeof(value)) for name, value in locals().items()),
#                              key= lambda x: -x[1])[:10]:
#         print(name + ': ' + str(size))
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

    print(asizeof_fmt(Brain_Data_allsubs_nn))

    print(asizeof_fmt(all_subs_nn_nifti))
    
    if subjs_to_use is None:
        subjs_to_use=len(np.unique(all_subs_nn_nifti_groups))

    sample_subject_items = np.unique(all_subs_nn_nifti_groups)[0:subjs_to_use] #get all of them
    sample_subject_vector = [i for i, x in enumerate(all_subs_nn_nifti_groups) if x in sample_subject_items]

    first_subs_nifti = nib.funcs.concat_images([all_subs_nn_nifti.slicer[...,s] for s in sample_subject_vector])
    first_subs_nifti_Y = all_subs_nn_nifti_Y[sample_subject_vector]
    first_subs_nifti = nil.image.clean_img(first_subs_nifti,detrend=False,standardize=True)
    first_subs_nifti_groups = all_subs_nn_nifti_groups[sample_subject_vector]

    del all_subs_nn_nifti
    gc.collect()
    

    decoder = Decoder(
        standardize= True,
        #scoring="r2",
        cv = GroupKFold(3), #inner CV
        mask=mask,
        n_jobs= cpus_available)

    first_subs_nifti_metadata = all_subs_nn_nifti_metadata.loc[sample_subject_vector,:]

    print("starting LeaveOneOut")
    #in this design, we're actually dealing with groups
    #we select group IDs and then grab the subjects
    #so we don't need to use LeaveOneGroupOut
    #the grouping is implicit
    cv_outer = LeaveOneOut()

    print("finished preprocessing")
    test_scores_same,tt_results,results_by_trainset_item = cv_train_test_sets(
        trainset_X=first_subs_nifti,
        trainset_y=first_subs_nifti_Y,
        trainset_groups=first_subs_nifti_groups,
        regressors = [decoder],
        cv=cv_outer,
        cpus_to_use=cpus_available
    )

    print(test_scores_same[0])
    print(np.mean(test_scores_same[0]))


    print('running one more time on whole dataset for beta map')
    
    regress_result = decoder.fit(
    y=first_subs_nifti_Y,X=first_subs_nifti,groups=first_subs_nifti_groups)

    weight_img = decoder.coef_img_['beta']

    print('finished learning')
    
    with open(results_filepath, 'wb') as handle:
        pickle.dump([test_scores_same,tt_results,results_by_trainset_item, regress_result],handle)


    print('saved.')
    
    

def apply_single_fit_dichotomized_prediction_loocv_and_save(
    results_filepath,
    brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    subjs_to_use = None #set this to get a subset, otherwise use all of them.
    ):
    #pd.set_option('display.max_rows', 99)
    test_train_set = pd.read_csv(train_test_markers_filepath)

    with open(brain_data_filepath, 'rb') as pkl_file:
        Brain_Data_allsubs = pickle.load(pkl_file)
    
    dev_wtp_io_utils.check_BD_against_test_train_set(Brain_Data_allsubs,test_train_set)

    #################################################
    #######PRE-PROCESS
    response_dichotomized = Brain_Data_allsubs.X['response'].copy()>Brain_Data_allsubs.X['response'].mean()
    Brain_Data_allsubs.Y = response_dichotomized.astype(int)
    print(Brain_Data_allsubs.Y.value_counts())
    Brain_Data_allsubs.Y[Brain_Data_allsubs.Y=='NULL']=None
    print(Brain_Data_allsubs.Y.value_counts())

#     import sys
#     for name, size in sorted(((name, sys.getsizeof(value)) for name, value in locals().items()),
#                              key= lambda x: -x[1])[:10]:
#         print(name + ': ' + str(size))
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

    print(asizeof_fmt(Brain_Data_allsubs_nn))

    print(asizeof_fmt(all_subs_nn_nifti))
    
    if subjs_to_use is None:
        subjs_to_use=len(np.unique(all_subs_nn_nifti_groups))

    sample_subject_items = np.unique(all_subs_nn_nifti_groups)[0:subjs_to_use] #get all of them
    sample_subject_vector = [i for i, x in enumerate(all_subs_nn_nifti_groups) if x in sample_subject_items]

    first_subs_nifti = nib.funcs.concat_images([all_subs_nn_nifti.slicer[...,s] for s in sample_subject_vector])
    first_subs_nifti_Y = all_subs_nn_nifti_Y[sample_subject_vector]
    first_subs_nifti = nil.image.clean_img(first_subs_nifti,detrend=False,standardize=True)
    first_subs_nifti_groups = all_subs_nn_nifti_groups[sample_subject_vector]

    del all_subs_nn_nifti
    gc.collect()
    

    decoder = Decoder(standardize= True,
                      #scoring="r2",
                      cv = GroupKFold(3), #inner CV
                      n_jobs= cpus_available)

    first_subs_nifti_metadata = all_subs_nn_nifti_metadata.loc[sample_subject_vector,:]

    print("starting LeaveOneOut")
    #in this design, we're actually dealing with groups
    #we select group IDs and then grab the subjects
    #so we don't need to use LeaveOneGroupOut
    #the grouping is implicit
    cv_outer = LeaveOneOut()

    print("finished preprocessing")
#     test_scores_same,tt_results,results_by_trainset_item = cv_train_test_sets(
#         trainset_X=first_subs_nifti,
#         trainset_y=first_subs_nifti_Y,
#         trainset_groups=first_subs_nifti_groups,
#         regressors = [decoder],
#         cv=cv_outer,
#         cpus_to_use=cpus_available
#     )

#     print(test_scores_same[0])
#     print(np.mean(test_scores_same[0]))

#     print('finished learning')

#     with open(results_filepath, 'wb') as handle:
#         pickle.dump([test_scores_same,tt_results,results_by_trainset_item],handle)

    print('running one more time on whole dataset for beta map')
    regress_result = dRegressor.fit(
    y=first_subs_nifti_Y,X=first_subs_nifti,groups=first_subs_nifti_groups)

    weight_img = decoder.coef_img_['beta']

    print('finished learning')

    with open(results_filepath, 'wb') as handle:
        pickle.dump([weight_img],handle)



    print('saved.')
    
    
