print("python initialized")


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
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut
import os, warnings

#custom thing I have set in my jupyter notebook task.
cpus_available = int(os.getenv('CPUS_PER_TASK'))
print(cpus_available)

pd.set_option('display.max_rows', 99)


test_train_set = pd.read_csv("../data/train_test_markers_20210601T183243.csv")

with open('../data/Brain_Data_2sns_60subs.pkl', 'rb') as pkl_file:
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
                         key= lambda x: -x[1])[:10]:
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

sample_subject_items = np.unique(all_subs_nn_nifti_groups)[0:60] #get all of them
sample_subject_vector = [i for i, x in enumerate(all_subs_nn_nifti_groups) if x in sample_subject_items]

first_subs_nifti = nib.funcs.concat_images([all_subs_nn_nifti.slicer[...,s] for s in sample_subject_vector])
first_subs_nifti_Y = all_subs_nn_nifti_Y[sample_subject_vector]
first_subs_nifti = nil.image.clean_img(first_subs_nifti,detrend=False,standardize=True)
first_subs_nifti_groups = all_subs_nn_nifti_groups[sample_subject_vector]

del all_subs_nn_nifti
gc.collect()

first_subs_nifti_metadata = all_subs_nn_nifti_metadata.loc[sample_subject_vector,:]

print("starting LeaveOneOut")
#in this design, we're actually dealing with groups
#we select group IDs and then grab the subjects
#so we don't need to use LeaveOneGroupOut
#the grouping is implicit
cv_outer = LeaveOneOut()

print("finished preprocessing")


def cv_train_test_sets(
    trainset_X, trainset_y, trainset_groups,
    regressors = None,
    testset_X = None,testset_y = None, testset_groups = None,
    param_grid=None,
    cpus_to_use=-2,
    cv = None):
    """
    uses a division of 'trainset' and 'testset' to allow different values to be trained and tested 
    in KFold Cross Validation. All the values are used for training and testing, but we use different ones.
    This enables us to e.g., pass in aggregated images for training and separate images for testing.
    
    trainset_X: x values applicalbe for TRAINING
    trainset_y
    trainset_groups: group allocations for the trainset dataset
    testset_X: values grouped into averages for testing
    testset_y
    cv: a Grouped cross-validator
    group_list: name of the groups
    """
    if cv is None:
        cv=KFold(n_splits=5)
        
    if param_grid is not None and regressors is not None:
        raise Exception('values for param_grid and regressors both passed, but param_grid is ignored if regressors is passed. choose one.')
    
    #if the groups we're using are actually the same.
    if (testset_X is None) and (testset_y is None):
        testset_X = trainset_X
        testset_y = trainset_y
        testset_groups = trainset_groups
        print('Groups are the same.')
        
    results_by_trainset_item = pd.DataFrame({
        'y': trainset_y,
        'group':trainset_groups,
        'y_pred':np.repeat(None,len(trainset_y))#,
        #'y_match':np.repeat(None,len(trainset_y))#just for debugging. delete.
    })
        

    groups_array = np.array(list(set(testset_groups)))
    assert(set(trainset_groups)==set(testset_groups))

    #the CV that the inner Regressor uses
    cv_inner = GroupKFold(3)
    if regressors is None:
        regressors = [DecoderRegressor(standardize= True,param_grid=param_grid,cv=cv_inner,scoring="r2",
                                      n_jobs=cpus_to_use)]
        print('using default regressor',end='. ')

    #we actually use KFold on the group names themselves, then filter across that
    #that's equivalent to doing a GroupedKFold on the data.
    test_scores = []
    results = []
    
    if type(cv)==type(LeaveOneOut()):
        outer_n=len(groups_array)
    else:
        outer_n = cv.get_n_splits()
    for i, x in enumerate(cv.split(groups_array)):
        train_i = x[0]
        test_i = x[1]
        print("fold " + str(i+1) + " of " + str(outer_n))
        
        fold_i_results = {}
        train_group_items, test_group_items = groups_array[train_i], groups_array[test_i]
        print('In order to test on a training group of ' +
              str(len(train_group_items)) + ' items, holding out the following subjects:' +
              str(test_group_items),end='. ')
#         print(
#             'held out ' + str(len(test_group_items)) + ' items and trained on ' + str(len(train_group_items)) + ' items',
#             end='. ')
        
        print('prepping fold data...',end='. ')
        #select training data from the averages
        #print('selecting training data',end='. ')
        train_selector = [i for i, x in enumerate(trainset_groups) if x in train_group_items]
        train_y = trainset_y[train_selector]
        train_X = nib.funcs.concat_images([trainset_X.slicer[...,s] for s in train_selector])
        train_groups = trainset_groups[train_selector]
        #print(train_X.shape,end='. ')
        #print(asizeof_fmt(train_X),end='. ')

        #select testing data from the individual values
        #print('selecting test data',end='. ')
        test_selector = [i for i, x in enumerate(testset_groups) if x in test_group_items]
        test_y = testset_y[test_selector]
        test_X = nib.funcs.concat_images([testset_X.slicer[...,s] for s in test_selector])
        test_groups = testset_groups[test_selector]
        #print(asizeof_fmt(test_X),end='. ')
        #print(test_X.shape,end='. ')


        print("regressing...",end='. ')
        print(asizeof_fmt(train_X),end='. ')
        
        val_scores = []
        #iterate through regressor objects.
        #this is my way of doing cross-validation across different regressors...
        hyper_scores = []
        train_results = {}
        inner_cv_results = {}
        for r_i, reg in enumerate(regressors):
            cur_r_results = {}
            print('trying regressor ' + str(r_i+1) + ' of ' + str(len(regressors)),end='. ')
            #if there is nested CV within this function the best hyper-paramters are already being chosen
            #we need only to finish the job by identifying the best overall regressor, as the final hyper-parameter
            reg.fit(y=train_y,X=train_X,groups=train_groups)
            print("predicting",end='. ')
            #hyper_score = reg.score(train_X,train_y)
            hyper_score = np.max([np.mean(param_values) for param_name, param_values in reg.cv_scores_.items()])
            #think there is a bug here. we should not have to be guessing/ignoring param names.
            #need to report this.
            
            hyper_scores = hyper_scores + [hyper_score]
            
            cur_r_results['hyper_score'] = hyper_score
            cur_r_results['cv_scores_'] = reg.cv_scores_
            cur_r_results['cv_params_'] = reg.cv_params_
            inner_cv_results[str(reg)] = cur_r_results
            
        fold_i_results['train_results']= inner_cv_results
        
        #identify which was the best
        #print(hyper_scores)
        #print(np.where([h==np.max(hyper_scores) for h in hyper_scores])[0][0])
        best_hyper_regressor = regressors[np.where([h==np.max(hyper_scores) for h in hyper_scores])[0][0]]
        
        #print(best_hyper_regressor)
        
        #now run JUST that one on this fold.
        
        
        #now predict on our test split
        test_score = best_hyper_regressor.score(test_X,test_y)
        test_y_pred = best_hyper_regressor.predict(test_X)
        fold_test_rawdata = pd.DataFrame({
            'y_obs':test_y,
            'y_pred':test_y_pred,
            'y_groups':test_groups
            
        })
        #results_by_trainset_item.loc[train_selector,'y_pred']
        results_by_trainset_item.loc[test_selector,'y_pred'] = test_y_pred
        #results_by_trainset_item.loc[test_selector,'y_match'] = test_y
        fold_i_results['fold_test_rawdata'] = fold_test_rawdata
        #so we can do scoring externally to this function.
        
        test_scores = test_scores+[test_score]
        print('test score was:',end='. ')
        print(test_score)
        
        results = results + [fold_i_results]

        del test_X
        del train_X
        gc.collect() #clean up. this is big data we're working with
        #https://stackoverflow.com/questions/1316767/how-can-i-explicitly-free-memory-in-python
        

    #We could use predefined split
#     warnings.warn(
#         "regressor was chosen based on train score across the entire train group, not the test fold of the inner CV." +
#         "Overall accuracy is not biased but this may yield a sub-optimal regressor selection." +
#         "The alternative, testing on the main holdout set, as described in the nilearn example, may overfit the data (see "+
#         "https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)." + 
#         "this problem could be addressed with the use of a PredefinedSplit." + 
#         "See https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.PredefinedSplit.html")

    return(test_scores,results,results_by_trainset_item)


test_scores_same,tt_results,results_by_trainset_item = cv_train_test_sets(
    trainset_X=first_subs_nifti,
    trainset_y=first_subs_nifti_Y,
    trainset_groups=first_subs_nifti_groups,
    cv=cv_outer,
    cpus_to_use=cpus_available
    
)

print(test_scores_same[0])
print(np.mean(test_scores_same[0]))

print('finished learning')
import pickle
with open("../data/cv_train_test_60subjs_sets_outer_n_loocv.pkl", 'wb') as handle:
    pickle.dump([test_scores_same,tt_results,results_by_trainset_item],handle)
    
    
print('saved.')
