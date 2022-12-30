import pandas as pd
import numpy as np
import scipy.io
import re
import warnings
import pickle
import datetime
from glob import glob
import yaml
import socket
from visualization import visualize_corr
import mvpa2
import math

import sys
import os
from outlier_detection import *


from IPython.core.display import display, HTML, Markdown

from sklearn.svm import SVC
from mvpa2.measures.base import CrossValidation
from mvpa2.clfs.meta import NFoldPartitioner
from mvpa2.clfs.svm import LinearCSVMC
from sklearn.calibration import CalibratedClassifierCV

from mvpa2.datasets.mri import fmri_dataset

class BehavioralDataNotFoundForBrainDataException(Exception):
    """Behavioral data could not be matched to a subject."""
    pass

from nilearn.masking import unmask


from mvpa2.mappers.flatten import mask_mapper
import nibabel as nib



sys.path.append(os.path.abspath("../../ml/"))

from sklearn.linear_model import Ridge

#import regex package

def read_yaml_for_host(file_path):
    hostname = socket.gethostname()
    with open(file_path, "r") as f:
        return yaml.safe_load(f)[hostname]

def do_Ridge(train_X,train_y,test_X,test_y):
    sklearn_reg = Ridge()

    #create the classifier with a probability function
    #https://mmuratarat.github.io/2019-10-12/probabilistic-output-of-svm#:~:text=SVMs%20don't%20output%20probabilities,the%20output%20to%20class%20probabilities.&text=For%20many%20problems%2C%20it%20is,of%20certainty%20about%20the%20answer.
    #we don't need this I'm doing my own probability estimate
    #hmmm, is this why the model is performing so well? the tuning?
    #sklearn_clf = CalibratedClassifierCV(clf_svc)
    #train
    sklearn_reg.fit(train_X, train_y)

    #get the _distance_ between predicted and actual
    #predict_y_prob = sklearn_reg.predict_proba(test_X)
    predict_y = sklearn_reg.predict(test_X)
    return(predict_y,sklearn_reg)


def do_regression(dataset,normalization=None,get_predict_and_prob=None):
    if get_predict_and_prob is None:
        get_predict_and_prob = do_Ridge
    logo=LeaveOneGroupOut()

    group_scores = {}
    sample_wise_results = []
    
    for train_index, test_index in logo.split(
        dataset.samples, dataset.sa.targets, dataset.sa.chunks):
        iteration_label = np.unique(dataset.sa.chunks[test_index])[0]

        #print(iteration_label, "; TRAIN:", len(train_index), " items; TEST:", test_index)
        print(".",end="",flush=True)

        #do train-test split
        train_X=dataset.samples[train_index]
        test_X = dataset.samples[test_index]
        train_y=dataset.sa.targets[train_index]
        test_y = dataset.sa.targets[test_index]
        #clf_svc = SVC()
        
        if normalization=="train_set_based":
            #get mean based on train set alone
            voxel_mean = np.mean(train_X,axis=0)
            voxel_sd = np.std(train_X,axis=0)
            #apply it to all.
            train_X=(train_X-voxel_mean)/voxel_sd
            test_X=(test_X-voxel_mean)/voxel_sd
            #print("normalizing")
        
        predict_y, sklearn_reg = get_predict_and_prob(train_X,train_y,test_X,test_y)
        
        
        mae = abs(predict_y - test_y)

        accuracy_score = np.sum(mae)/len(mae)
        #can we do a sample-wise table?

        group_scores[iteration_label] = accuracy_score
        sample_wise_results_iter = pd.DataFrame({
            'chunks':[iteration_label]*len(test_y),
            'target_y':test_y,
            'pred_y':predict_y,
            'mae' : accuracy_score
            #'pred_y_forced_choice':forced_choice_predictions
        })
#         #add the class-wise probabilities
#         for cls in sklearn_clf.classes_:
#             sample_wise_results_iter['pred_prob_' + cls] = proba_dict[cls]
            
        sample_wise_results = sample_wise_results + [sample_wise_results_iter]
        
    #need to create one more classifier to return.
    #we test and train on the same here, which is OK, because we don't use this to assess performance
    y_predict, model_final =get_predict_and_prob(
        dataset.samples,dataset.sa.targets,dataset.samples,dataset.sa.targets)
            
    sample_wise_results_df = pd.concat(sample_wise_results)
    return({'sample_wise':sample_wise_results_df,'group_wise':group_scores,'model':model_final})


from mvpa_pipeline_utils import get_Brain_Data_betas_as_mvpa_for_sub, import_beta_series_pymvpa2, sa_to_df

from sklearn.model_selection import LeaveOneGroupOut

from sklearn.svm import LinearSVC
from scipy.stats import ttest_1samp, pearsonr

def pearson_img_series(img_series,img_cor):
    #iterate through the series
    img_length = img_series.shape[0]
    pearson_img_result = [0]*img_length
    
    for img_i in range(img_length):
        #now get the similarity
        #print(Brain_Data_allsubs[img_i,].samples.flatten().shape)
        #print(linearSVC_results['classifier'].coef_.flatten().shape)
        pearson_result = pearsonr(
            img_series[img_i,].flatten(),
            img_cor.flatten()
        )
        #we need the positive and the negative image to do this correctly
        #we're just going to assume that the positive should come first, that the classifier
        pearson_img_result[img_i] = [-pearson_result[0],pearson_result[0]]
        #print(pearson_result[0])
        
    return(pearson_img_result)

def do_LinearSVC(train_X,train_y,test_X,test_y):
    sklearn_clf = LinearSVC(penalty='l2', max_iter=1e4)
    #same as v3, my nilearn learner integrated with nltools
    #https://nilearn.github.io/modules/generated/nilearn.decoding.Decoder.html
    
    #sklearn_clf = CalibratedClassifierCV(clf_svc)
    #train
    sklearn_clf.fit(train_X, train_y)

    #get the _probability_ we fall into each class
    #we'll use similarity/correlation here.
    predict_y_prob = pearson_img_series(test_X,sklearn_clf.coef_)#sklearn_clf.predict_proba(test_X)
    predict_y = sklearn_clf.predict(test_X)
    return(predict_y,predict_y_prob,sklearn_clf)

def do_LinearSVC_proba(train_X,train_y,test_X,test_y,svc_kernel='linear'):
    sklearn_clf = SVC(kernel=svc_kernel,probability=True)

    #create the classifier with a probability function
    #https://mmuratarat.github.io/2019-10-12/probabilistic-output-of-svm#:~:text=SVMs%20don't%20output%20probabilities,the%20output%20to%20class%20probabilities.&text=For%20many%20problems%2C%20it%20is,of%20certainty%20about%20the%20answer.
    #we don't need this I'm doing my own probability estimate
    #hmmm, is this why the model is performing so well? the tuning?
    #sklearn_clf = CalibratedClassifierCV(clf_svc)
    #train
    sklearn_clf.fit(train_X, train_y)

    #get the _probability_ we fall into each class
    predict_y_prob = sklearn_clf.predict_proba(test_X)
    predict_y = sklearn_clf.predict(test_X)
    return(predict_y,predict_y_prob,sklearn_clf)

def do_LinearSVC_proba_poly(train_X,train_y,test_X,test_y):
    return(do_LinearSVC_proba(train_X,train_y,test_X,test_y,svc_kernel='poly'))

def do_LinearSVC_proba_sigmoid(train_X,train_y,test_X,test_y):
    return(do_LinearSVC_proba(train_X,train_y,test_X,test_y,svc_kernel='sigmoid'))



def do_SVC(train_X,train_y,test_X,test_y):
    sklearn_clf = SVC(probability=True)

    #create the classifier with a probability function
    #https://mmuratarat.github.io/2019-10-12/probabilistic-output-of-svm#:~:text=SVMs%20don't%20output%20probabilities,the%20output%20to%20class%20probabilities.&text=For%20many%20problems%2C%20it%20is,of%20certainty%20about%20the%20answer.
    #we don't need this I'm doing my own probability estimate
    #hmmm, is this why the model is performing so well? the tuning?
    #sklearn_clf = CalibratedClassifierCV(clf_svc)
    #train
    sklearn_clf.fit(train_X, train_y)

    #get the _probability_ we fall into each class
    predict_y_prob = sklearn_clf.predict_proba(test_X)
    predict_y = sklearn_clf.predict(test_X)
    return(predict_y,predict_y_prob,sklearn_clf)


def do_forced_choice(dataset,normalization=None,get_predict_and_prob=None):
    if get_predict_and_prob is None:
        get_predict_and_prob = do_SVC
    logo=LeaveOneGroupOut()

    group_scores = {}
    sample_wise_results = []
    
    for train_index, test_index in logo.split(
        dataset.samples, dataset.sa.targets, dataset.sa.chunks):
        iteration_label = np.unique(dataset.sa.chunks[test_index])[0]

        #print(iteration_label, "; TRAIN:", len(train_index), " items; TEST:", test_index)
        print(".",end="",flush=True)

        #do train-test split
        train_X=dataset.samples[train_index]
        test_X = dataset.samples[test_index]
        train_y=dataset.sa.targets[train_index]
        test_y = dataset.sa.targets[test_index]
        #clf_svc = SVC()
        
        if normalization=="train_set_based":
            #get mean based on train set alone
            voxel_mean = np.mean(train_X,axis=0)
            voxel_sd = np.std(train_X,axis=0)
            #apply it to all.
            train_X=(train_X-voxel_mean)/voxel_sd
            test_X=(test_X-voxel_mean)/voxel_sd
            #print("normalizing")
        
        predict_y, y_class_match, sklearn_clf = get_predict_and_prob(train_X,train_y,test_X,test_y)
        
        
        #need to label the output of the probability as CorrectStop and CorrectGo based on the classnames
        #iterate through each class
        proba_dict = {}
        for i, cls in enumerate(sklearn_clf.classes_):
            proba_dict[cls] = [x[i] for x in y_class_match]
            
        class_0 = sklearn_clf.classes_[0]
        class_1 = sklearn_clf.classes_[1]

        #find out which one of the two images is most likely to be CorrectGo
        class_0_choice_index = np.argmax(proba_dict[class_0])
        #now put that into a vector
        forced_choice_predictions = [class_1]*2
        forced_choice_predictions[class_0_choice_index] = class_0
        accuracy_score = np.sum([pred==target for pred,target in zip(forced_choice_predictions,test_y)])/len(test_y)
        #can we do a sample-wise table?

        group_scores[iteration_label] = accuracy_score
        sample_wise_results_iter = pd.DataFrame({
            'chunks':[iteration_label]*len(test_y),
            'target_y':test_y,
            'pred_y':predict_y,
            'pred_y_forced_choice':forced_choice_predictions
        })
        #add the class-wise probabilities
        for cls in sklearn_clf.classes_:
            sample_wise_results_iter['pred_prob_' + cls] = proba_dict[cls]
            
        sample_wise_results = sample_wise_results + [sample_wise_results_iter]
        
    #need to create one more classifier to return.
    #we test and train on the same here, which is OK, because we don't use this to assess performance
    y_predict, y_class_match, clf_svc_final =get_predict_and_prob(
        dataset.samples,dataset.sa.targets,dataset.samples,dataset.sa.targets)
            
    sample_wise_results_df = pd.concat(sample_wise_results)
    return({'sample_wise':sample_wise_results_df,'group_wise':group_scores,'classifier':clf_svc_final})

def setup_metadata(bd,target_attri_label = 'condition_label', standardize=False):
    #set up chunks and targets so we can do the learning.
    attribute_df = sa_to_df(bd.sa)
    pd.concat([attribute_df['subject'],attribute_df['wave']],axis=1)
    chunk = attribute_df['subject']+"_" + attribute_df['wave'].astype(str)
    bd.sa['chunks'] = list(chunk)
    if standardize:
        target_data = bd.sa[target_attri_label].value
        target_data_mean = np.nanmean(target_data)
        target_data_std = np.nanstd(target_data)
        target_data_norm = (target_data-target_data_mean)/target_data_std
        bd.sa['targets'] = list(target_data_norm)
    else:
        bd.sa['targets'] = list(bd.sa[target_attri_label].value)

    return(bd)


def inv_log_transform(series):
    series=series.copy()
    not_na_vals = np.isnan(series)==False
    log_vals = [math.log(1-x) for x in (series[not_na_vals])]
    series[not_na_vals] = log_vals
    return(log_vals)




def print_forced_choice_results(
    forced_choice_results,
    individual_differences,
    neural_measures = ['pred_prob_CorrectStop'],
    behavioral_measures = ['bf_1','cancer_promoting_minus_preventing_FFQ','TESQ_E_sum'],#['RTFS_factor_1','RTFS_factor_2','RTFS_f1_minus_f2']
    target_y="CorrectStop"
):
    prediction = np.mean(forced_choice_results['sample_wise']['target_y']==forced_choice_results['sample_wise']['pred_y'])
    forced_choice_prediction = np.mean(forced_choice_results['sample_wise']['target_y']==forced_choice_results['sample_wise']['pred_y_forced_choice'])
    print((prediction, forced_choice_prediction))
    
    sample_wise_results = forced_choice_results['sample_wise']
    cs_cs_prob = sample_wise_results.loc[sample_wise_results.target_y==target_y]

    individual_differences['subj_wave'] = individual_differences.subject+"_"+individual_differences.wave.astype(str)
    full_dataset_cs = individual_differences.merge(cs_cs_prob,how='outer',left_on='subj_wave',right_on='chunks')
    
    full_dataset_cs = remove_selected_outliers(
        full_dataset_cs,
        behavioral_measures + neural_measures,
    show_plot=False)
    
    #https://docs.google.com/presentation/d/10tKHw1VF2WiMapvKXkh2C9VeFHk6iCjTmc0tDTiugOk/edit#slide=id.g11512b79600_0_10
    for nm in neural_measures:
        for bm in behavioral_measures:
            visualize_corr(nm, bm, full_dataset_cs)

def print_regression_results(
    forced_choice_results,
    neural_measures = ['mae'],
    behavioral_measures = ['bf_1','cancer_promoting_minus_preventing_FFQ','TESQ_E_sum']
):
    sample_wise_results = forced_choice_results['sample_wise']
#    cs_cs_prob = sample_wise_results.loc[sample_wise_results.target_y=='CorrectStop']

    individual_differences['subj_wave'] = individual_differences.subject+"_"+individual_differences.wave.astype(str)
    full_dataset_cs = individual_differences.merge(sample_wise_results,how='outer',left_on='subj_wave',right_on='chunks')
    print(full_dataset_cs.columns)
    full_dataset_cs = remove_selected_outliers_mvpa_tesq_study(
        full_dataset_cs,neural_measures = neural_measures,
        show_plot=False)
    
    #https://docs.google.com/presentation/d/10tKHw1VF2WiMapvKXkh2C9VeFHk6iCjTmc0tDTiugOk/edit#slide=id.g11512b79600_0_10
    for nm in neural_measures:
        for bm in behavioral_measures:
            visualize_corr(nm,bm,full_dataset_cs)
    
    

    
