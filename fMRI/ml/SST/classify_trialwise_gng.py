import gc
import sys
import os
import pandas as pd
import numpy as np


sys.path.append(os.path.abspath("../../ml/"))
from apply_loocv_and_save import load_and_preprocess
from dev_utils import read_yaml_for_host
import warnings


config_data = read_yaml_for_host("sst_config.yml")

import multiprocessing
import math
import nibabel as nib
import nilearn as nl
from nilearn.decoding import DecoderRegressor,Decoder
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut
cpus_available = multiprocessing.cpu_count()

cpus_to_use = min(cpus_available-1,math.floor(0.9*cpus_available))
print(cpus_to_use)


from sklearn.metrics import precision_recall_fscore_support
from dev_wtp_io_utils import cv_train_test_sets, asizeof_fmt
from nilearn.decoding import DecoderRegressor,Decoder

nonbids_data_path = config_data['nonbids_data_path']
ml_data_folderpath = nonbids_data_path + "fMRI/ml"



def trialtype_resp_trans_func(X):
    return(X.trial_type)

def main(normalize_across_features=True):

    brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_betaseries_40subs_correct_cond.pkl'
    #brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_betaseries_15subs_correct_cond.pkl'
    print(brain_data_filepath)
    warnings.warn("not sure if this file holds up--it was created in 2021; need to see if it's still valid")
    train_test_markers_filepath = ml_data_folderpath + "/train_test_markers_20220818T144138.csv"

    all_subjects = load_and_preprocess(
        brain_data_filepath,
        train_test_markers_filepath,
        subjs_to_use = None,
        response_transform_func = trialtype_resp_trans_func,
        clean=None)

    if normalize_across_features:
        print("normalizing across features...")
        #get average signal across first 3 axes of the array
        img_avg_signal = all_subjects['X'].get_fdata().mean(axis=(0,1,2))
        img_std_signal = all_subjects['X'].get_fdata().std(axis=(0,1,2))

        print("creating new arrays...")
        series_avg_signal_ndarray =  np.array([np.tile(x,all_subjects['X'].shape[0:3]) for x in img_avg_signal])
        #rotate the array so that the last axis is time
        series_avg_signal_ndarray = np.moveaxis(series_avg_signal_ndarray,0,-1)
        #series_avg_signal_ndarray.shape


        series_std_signal_ndarray =  np.array([np.tile(x,all_subjects['X'].shape[0:3]) for x in img_std_signal])
        #rotate the array so that the last axis is time
        series_std_signal_ndarray = np.moveaxis(series_std_signal_ndarray,0,-1)
        #series_std_signal_ndarray.shape

        print("creating nifti images...")
        #now create nifti images out of them
        avg_img = nl.image.new_img_like(all_subjects['X'].slicer[:,:,:,0], series_avg_signal_ndarray)
        std_img = nl.image.new_img_like(all_subjects['X'].slicer[:,:,:,0], series_std_signal_ndarray)

        print("doing the math...")
        #do the math
        all_subjects=nl.image.math_img("(img-avg)/std", img=all_subject['X'], avg=avg_img, std=std_img)
        #remove unneeded files
        print('removing unneeded files...')
        del avg_img
        del std_img
        del series_avg_signal_ndarray
        del series_std_signal_ndarray
        gc.collect()


    warnings.warn("the data hasn't been cleaned at any point. the fMRIPrep cleaning pipeline has been applied; nothing else has been.")

    #convert the y array to an integer array representing the string values of the y array
    all_subjects['y_cat'] = all_subjects['y'].astype('category')
    all_subjects['y_int']=all_subjects['y_cat'].cat.codes
    # get the PFC mask
    mask_nifti = nib.load(ml_data_folderpath + '/prefrontal_cortex.nii.gz')


    ### TRAINING

    dec_main = Decoder(standardize=True,cv=GroupKFold(3),scoring='roc_auc',n_jobs=cpus_to_use,mask=mask_nifti)
    cv_results = cv_train_test_sets(
        trainset_X = all_subjects['X'],
        trainset_y = all_subjects['y_int'],
        trainset_groups = all_subjects['metadata']['subject'],
        decoders = [dec_main],
        cv=KFold(n_splits=3) # we use KFold, not GroupKfold, because it's splitting on Group anyway
        )

    cv_results_dict = {
        'test_scores':cv_results[0],
        'results':cv_results[1],
        'results_by_trainset_item':cv_results[2],
    }
    

    #get roc_auc
    from sklearn.metrics import roc_auc_score
    print("cross-validated performance")
    #get precision and recall
    print("precision, recall, f1, support:")
    print(precision_recall_fscore_support(
        cv_results_dict['results_by_trainset_item']['y'],
    cv_results_dict['results_by_trainset_item']['y_pred'].astype(int),average='macro'))
    print("roc_auc:")
    print(roc_auc_score(
        cv_results_dict['results_by_trainset_item']['y'],
        cv_results_dict['results_by_trainset_item']['y_pred']))

    print("-----\n\n")
    print("training performance (overfit):")
    final_prediction = dec_main.predict(all_subjects['X'])


    #pd.DataFrame({'obs':trainset_y,'pred':final_prediction}).value_counts()
    #get precision and recallg
    print("precision, recall, f1, support:")
    print(precision_recall_fscore_support(all_subjects['y_int'],final_prediction,average='macro'))

    #get roc_auc
    from sklearn.metrics import roc_auc_score
    print("roc_auc:")
    print(roc_auc_score(all_subjects['y_int'],final_prediction))

if __name__ == "__main__":
    main()