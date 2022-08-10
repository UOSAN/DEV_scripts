import pickle
from IPython.core.display import display, HTML, Markdown
import os
import sys
sys.path.append(os.path.abspath("../../ml/"))

from apply_loocv_and_save import *
from dev_wtp_io_utils import *

from nilearn.decoding import Decoder
from sklearn.model_selection import StratifiedKFold
from random import randint
import math
import pandas as pd
import numpy as np

def get_subject_discriminability(sample_subject,train_test_markers_filepath, brain_data_filepath, resp_trans_func = None,
                                 mask=None,splits_to_use = 3
                                 ):
    min_splits = 3
    # iterate through each subject; for each subject:
    display(Markdown("loading subject " + sample_subject))
    #print(mask)

    subj_i_processed_data = load_and_preprocess(
        brain_data_filepath,
        train_test_markers_filepath,
        subjs_to_use = [sample_subject],
        response_transform_func = resp_trans_func,
        clean="standardize")
    
    print(subj_i_processed_data['y'].value_counts())
    
    print("setting up decoder...")
    #we use stratified Kfold
    smallest_class_size = min(subj_i_processed_data['y'].value_counts())
    class_count = len(np.unique(subj_i_processed_data['y']))
    
    #split according to the number of members of the smallest class.
    if splits_to_use=="min_class":
        splits_to_use = smallest_class_size
    
    if (smallest_class_size< min_splits) or (class_count<2):
        print("not enough items in the smallest class or not enough classes. cannot proceed for this subject.")
        return(None)
        #could do one split per correct-stop
        #because there are generally very few of them
        
    print("using StratifiedKFold with " + str(splits_to_use) + " splits")
        
    skf = StratifiedKFold(n_splits = splits_to_use,random_state= randint(0,math.pow(2,32)),
                          shuffle=True)
        #for testing for now we'll use 3
        
    #do this separately for each outcome group
    decoder = Decoder(standardize=True, 
                      cv = skf, mask = mask,
                      n_jobs = min(cpus_to_use, splits_to_use),#verbose=10,
                      scoring='accuracy'
                     )

    display(Markdown("fitting"))
    #get overfit individual predictions--only way we can assess individual predictions
    decoder_result = decoder.fit(X=subj_i_processed_data['X'],y=subj_i_processed_data['y'])
    
    display(Markdown("evaluating"))
    
    predictions = decoder.predict(subj_i_processed_data['X'])
    y_pred_vs_obs = pd.DataFrame({'y_obs':subj_i_processed_data['y'],'y_pred':predictions})
    overfit_accuracy = np.sum(y_pred_vs_obs['y_obs']==y_pred_vs_obs['y_pred'])/len(y_pred_vs_obs['y_obs'])
    
    #get mean_cv_scores - cross-validated scores but I'm not sure what they mean becuase the package is vague
    mean_cv_scores = np.mean([np.mean(c_scores) for c_name, c_scores in decoder.cv_scores_.items()])
    
    #alternative to this is to do our own cv stuff
    subj_discrim_results = {
        'mean_cv_scores':mean_cv_scores,
        'overfit_accuracy':overfit_accuracy,
        'overfit_y_pred_vs_obs': y_pred_vs_obs,
        'cv_splits': splits_to_use,
        'n_samples': len(subj_i_processed_data['y'])
#        'decoder_object' : decoder
    }
    display(subj_discrim_results)


    return(subj_discrim_results)


def get_subject_discriminability_with_cache(sample_subject,run_desc,subject_discrim_args,cache_folder= None, ml_data_folderpath=None):
    if cache_folder is None:
        cache_folder = (ml_data_folderpath + "/SST/discriminability_cache/" + run_desc + "/")
        
    results_filepath = cache_folder + "dtt_results_" + sample_subject + ".pkl"
    
    print(results_filepath)
    
    if os.path.exists(results_filepath) is False:
        subj_discrim_results = get_subject_discriminability(sample_subject,**subject_discrim_args)
        
        if os.path.exists(cache_folder)==False:
            os.mkdir(cache_folder)
        with open(results_filepath, 'wb') as handle:
            pickle.dump(subj_discrim_results,handle)
    else:
        subj_discrim_results=pickle.load(open(results_filepath,'rb'))
        print("pre-loaded.",flush=True)
        
    print(subj_discrim_results,flush=True)
    return(subj_discrim_results)
    
    
def get_all_subjs_discriminability_whole_brain(subj_list, subject_discrim_args):
    results_dict = {}

    for sample_subject in subj_list:
        display(Markdown(sample_subject))
        run_desc = 'v1_whole_brain'
        results_dict[sample_subject] = get_subject_discriminability_with_cache(sample_subject,run_desc,subject_discrim_args=subject_discrim_args)
        
    summary_results = pd.concat([pd.DataFrame({
        'subid':k,
        'overfit_accuracy':[v['overfit_accuracy']],
        'mean_cv_scores':[v['mean_cv_scores']]}) 

                                 for k,v in results_dict.items() if v is not None])
    
    return(summary_results)

def get_all_subjs_discriminability_masked(subj_list,run_desc, ml_data_folderpath, subject_discrim_args):
    results_dict = {}

    for sample_subject in subj_list:
        print(sample_subject,flush=True)
        results_dict[sample_subject] = get_subject_discriminability_with_cache(
            sample_subject,run_desc,ml_data_folderpath=ml_data_folderpath, subject_discrim_args = subject_discrim_args)
        
        print(results_dict[sample_subject])
        
    summary_results = pd.concat([pd.DataFrame({
        'subid':k,
        'overfit_accuracy':[v['overfit_accuracy']],
        'mean_cv_scores':[v['mean_cv_scores']]}) 

                                 for k,v in results_dict.items() if v is not None])
    
    return(summary_results)

