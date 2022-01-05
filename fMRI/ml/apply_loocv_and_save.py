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
from dev_wtp_io_utils import cv_train_test_sets, asizeof_fmt
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut, LeaveOneGroupOut
import os, warnings
import pickle
from nilearn.decoding import DecoderRegressor, Decoder

cpus_available = int(os.getenv('CPUS_PER_TASK'))
#custom thing I have set in my jupyter notebook task.
print(cpus_available)
cpus_to_use = cpus_available-1

def apply_loocv_and_save(
    results_filepath,
    brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    subjs_to_use = None, #set this to get a subset, otherwise use all of them.
    response_transform_func = None,
    mask=None,
    decoderConstructor=DecoderRegressor
    ):
    

    preprocessed_data = load_and_preprocess(brain_data_filepath,train_test_markers_filepath,subjs_to_use,response_transform_func)
    
#     return(
#         {
#             'X':first_subs_nifti,
#             'y':first_subs_nifti_Y
#             'groups':first_subs_nifti_groups
#             'metadata':first_subs_nifti_metadata
#         }
#     )

    first_subs_nifti_Y = preprocessed_data['y']
    first_subs_nifti = preprocessed_data['X']
    first_subs_nifti_groups = preprocessed_data['groups']

    print("starting LeaveOneOut")

    cv_inner = GroupKFold(3)
    
#     if mask is not None:
#         from nilearn import plotting
#         plotting.plot_img(mask)

    decoder = decoderConstructor(
        standardize= True,cv=cv_inner,
        mask=mask,
        n_jobs=cpus_to_use)
    
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
        decoders=[decoder],
        cv=cv_outer,
        cpus_to_use=cpus_available

    )

    print(test_scores_same[0])
    print(np.mean(test_scores_same[0]))
    
    print('running one more time on whole dataset for beta map')
    regress_result = decoder.fit(
    y=first_subs_nifti_Y,X=first_subs_nifti,groups=first_subs_nifti_groups)

    if type(decoder)==DecoderRegressor:
        weight_img = decoder.coef_img_['beta']
    else:
        weight_img = decoder.coef_img_

    print('finished learning')

    with open(results_filepath, 'wb') as handle:
        pickle.dump([test_scores_same,tt_results,results_by_trainset_item,weight_img],handle)


    print('saved.')
    
def apply_single_fit_and_save(
    results_filepath,
    brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    subjs_to_use = None, #set this to get a subset, otherwise use all of them.
    response_transform_func = None,
    mask=None
    ):
    
    

    preprocessed_data = load_and_preprocess(brain_data_filepath,train_test_markers_filepath,subjs_to_use,response_transform_func)
    
    train_y = preprocessed_data['y']
    train_X = preprocessed_data['X']
    train_groups = preprocessed_data['groups']
    

    
    from nilearn.decoding import DecoderRegressor
    dRegressor = DecoderRegressor(
        standardize= True,cv=LeaveOneGroupOut(),scoring="r2",
        mask=mask,
        n_jobs=cpus_to_use,
        verbose=1)


    print("starting LeaveOneOut")
    #in this design, we're actually dealing with groups
    #we select group IDs and then grab the subjects
    #so we don't need to use LeaveOneGroupOut
    #the grouping is implicit

    print("finished preprocessing")


    
    print('running one more time on whole dataset for beta map')
    dRegressor.fit(
    y=train_y,X=train_X,groups=train_groups)
    
    train_score = dRegressor.score(train_X,train_y)
    train_y_pred = dRegressor.predict(train_X)

    if type(dRegressor)==DecoderRegressor:
        weight_img = dRegressor.coef_img_['beta']
    else:
        weight_img = dRegressor.coef_img_
    print('finished learning')

    with open(results_filepath, 'wb') as handle:
        pickle.dump({
            'regressor':dRegressor,
            'weight_img':weight_img,
            'obs':train_y,
            'train_train_score':train_score,
            'train_y_pred': train_y_pred,
            'metadata':preprocessed_data['metadata']
        },handle)


    print('saved.')
    
def load_and_preprocess(brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    subjs_to_use = None, #set this to get a subset, otherwise use all of them.
    response_transform_func = None,
    clean = "standardize"
):



    test_train_set = pd.read_csv(train_test_markers_filepath)

    with open(brain_data_filepath, 'rb') as pkl_file:
        Brain_Data_allsubs = pickle.load(pkl_file)
    
    dev_wtp_io_utils.check_BD_against_test_train_set(Brain_Data_allsubs,test_train_set)
    
    #################################################
    #######PRE-PROCESS


    
    if response_transform_func is None:
        Brain_Data_allsubs.Y = Brain_Data_allsubs.X['response'].copy()
    else:
        Brain_Data_allsubs.Y = response_transform_func(Brain_Data_allsubs.X)
    
        
    #print(Brain_Data_allsubs.Y.value_counts())
    Brain_Data_allsubs.Y[Brain_Data_allsubs.Y=='NULL']=None
    #print(Brain_Data_allsubs.Y.value_counts())
    

    import sys
    for name, size in sorted(((name, sys.getsizeof(value)) for name, value in locals().items()),
                             key= lambda x: -x[1])[:10]:
        print(name + ': ' + str(size))
    #print(Brain_Data_allsubs.Y.isnull().value_counts())
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
    #print(asizeof_fmt(Brain_Data_allsubs))
    #print(asizeof_fmt(Brain_Data_allsubs_nn)) 

    
    del Brain_Data_allsubs
    del Brain_Data_allsubs_nn
    #del Brain_Data_allsubs_grouped
    gc.collect()

    
    if subjs_to_use is None:
        first_subs_nifti = all_subs_nn_nifti
        first_subs_nifti_Y = all_subs_nn_nifti_Y
        first_subs_nifti_groups = all_subs_nn_nifti_groups
        first_subs_nifti_metadata = all_subs_nn_nifti_metadata
    elif type(subjs_to_use)==int:
        print("using " +  str(subjs_to_use) + " subjects")
        sample_subject_items = np.unique(all_subs_nn_nifti_groups)[0:subjs_to_use] #get all of them
        sample_subject_vector = [i for i, x in enumerate(all_subs_nn_nifti_groups) if x in sample_subject_items]

        first_subs_nifti = nib.funcs.concat_images([all_subs_nn_nifti.slicer[...,s] for s in sample_subject_vector])
        first_subs_nifti_Y = all_subs_nn_nifti_Y[sample_subject_vector]
        first_subs_nifti_groups = all_subs_nn_nifti_groups[sample_subject_vector]
        first_subs_nifti_metadata = all_subs_nn_nifti_metadata.loc[sample_subject_vector,:]
    else: #named subjects, assume subjs_to_use is iterable
        sample_subject_vector = [i for i, x in enumerate(all_subs_nn_nifti_groups) if x in subjs_to_use]

        first_subs_nifti = nib.funcs.concat_images([all_subs_nn_nifti.slicer[...,s] for s in sample_subject_vector])
        first_subs_nifti_Y = all_subs_nn_nifti_Y[sample_subject_vector]
        first_subs_nifti_groups = all_subs_nn_nifti_groups[sample_subject_vector]
        first_subs_nifti_metadata = all_subs_nn_nifti_metadata.loc[sample_subject_vector,:]
        

    if clean=="standardize":
        first_subs_nifti = nil.image.clean_img(first_subs_nifti,detrend=False,standardize=True)

    return(
        {
            'X':first_subs_nifti,
            'y':first_subs_nifti_Y,
            'groups':first_subs_nifti_groups,
            'metadata':first_subs_nifti_metadata
        }
    )

    
    
