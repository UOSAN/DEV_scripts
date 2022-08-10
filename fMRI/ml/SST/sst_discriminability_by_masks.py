from discriminability_tools import *

import pickle
from IPython.core.display import display, HTML, Markdown
from nilearn.decoding import Decoder
from sklearn.model_selection import StratifiedKFold
from random import randint
import math

import sys
import os
import pandas as pd
import gc

sys.path.append(os.path.abspath("../../ml/"))

from apply_loocv_and_save import *
from dev_wtp_io_utils import *
import gc
import nibabel as nib

from os import path
import multiprocessing
import math



nonbids_data_path = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/"
ml_data_folderpath = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/ml"
train_test_markers_filepath = ml_data_folderpath + "/train_test_markers_20210601T183243.csv"
test_train_df = pd.read_csv(train_test_markers_filepath)

all_sst_events= pd.read_csv(ml_data_folderpath +"/SST/" + "all_sst_events.csv")


dataset_name = 'conditions'

from nilearn.decoding import DecoderRegressor, Decoder

script_path = '/gpfs/projects/sanlab/shared/DEV/DEV_scripts/fMRI/ml'
# HRF 2s

#get a PFC mask
#pfc_mask = create_mask_from_images(get_pfc_image_filepaths(ml_data_folderpath + "/"),threshold=10)


def trialtype_resp_trans_func(X):
    return(X.trial_type)

#cpus_available = int(os.getenv('CPUS_PER_TASK'))

#custom thing I have set in my jupyter notebook task.
cpus_available = multiprocessing.cpu_count()

cpus_to_use = min(cpus_available-1,math.floor(0.9*cpus_available))
print(cpus_available, cpus_to_use)

from analyze_results import remove_selected_outliers
from scipy.stats import pearsonr,spearmanr
from matplotlib import pyplot

def remove_selected_outliers_tesq_study(ind_div_combined,show_plot=False):
    idc_outliers_removed = remove_selected_outliers(ind_div_combined,
    ['discriminability_overfit_accuracy','discriminability_mean_cv_scores',
        'BFI_extraversion','RMQ_locomotion','ses_aggregate','PLAN_cognitive_strategies',
     'SST_SSRT','BIS_11','BSCS','TESQ_E_suppression', 'TESQ_E_avoidance_of_temptations', 
     'TESQ_E_goal_deliberation', 'TESQ_E_controlling_temptations', 'TESQ_E_distraction',
     'TESQ_E_goal_and_rule_setting','EDM','RS','TRSQ','ROC_Crave_Regulate_Minus_Look',
     'SRHI_unhealthy',
     'cancer_promoting_minus_preventing_FFQ','bf_1'],
    show_plot=show_plot)
    return(idc_outliers_removed)

def display_discriminability_correlations(ind_div_combined_3sd):
    for neural_var in ['discriminability_overfit_accuracy','discriminability_mean_cv_scores']:
        display(Markdown("### " + neural_var))
        for correlate in [#'BFI_extraversion','RMQ_locomotion','ses_aggregate','PLAN_cognitive_strategies',
                          'SST_SSRT',#'BIS_11','BSCS',
                          'TESQ_E_suppression', 'TESQ_E_avoidance_of_temptations', 
                          'TESQ_E_goal_deliberation', 'TESQ_E_controlling_temptations', 'TESQ_E_distraction',
                          'TESQ_E_goal_and_rule_setting',
                        #'EDM','RS','TRSQ','ROC_Crave_Regulate_Minus_Look','SRHI_unhealthy'
        ]:
            display(Markdown("#### " + correlate))
            nan_rows = np.isnan(ind_div_combined_3sd[correlate]) | np.isnan(ind_div_combined_3sd[neural_var])
            cor2way_df = ind_div_combined_3sd.loc[nan_rows==False,]
            pearson_result = pearsonr(cor2way_df[neural_var],cor2way_df[correlate])
            display(HTML("r=" + format(pearson_result[0],".2f") +"; p-value=" + format(pearson_result[1],".4f")))
            spearman_result = spearmanr(cor2way_df[neural_var],cor2way_df[correlate])
            display(HTML("rho=" + format(spearman_result[0],".2f") +"; p-value=" + format(spearman_result[1],".4f")))
            cplot = pyplot.scatter(cor2way_df[neural_var],cor2way_df[correlate])
            cplot.axes.set_xlabel(neural_var)
            cplot.axes.ylabel=correlate
            pyplot.show()
            
            
dataset_name = 'conditions'


brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_betaseries_84subs_correct_cond.pkl'
#brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_betaseries_58subs_correct_cond.pkl'
#brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_conditions_43subs_correct_cond.pkl'

## get subject IDs in the dataset

all_subjects = load_and_preprocess(
    brain_data_filepath,
    train_test_markers_filepath,
    subjs_to_use = None,
    response_transform_func = trialtype_resp_trans_func,
    clean=None)

all_subjects['groups']

subj_list = np.unique(all_subjects['groups'])

del all_subjects
gc.collect()

summary_results_list = {}
discriminability_version_id="v_1_"

#now dow the main loop
#have to do it twice becuase we have different masks which require different thresholds.

neurosynth_mask_folder = ml_data_folderpath + "/masks/response_inhibition_related/"
neurosynth_mask_name_list = os.listdir(neurosynth_mask_folder)
for mask_filename in neurosynth_mask_name_list:
    if os.path.isdir(neurosynth_mask_folder + mask_filename):
        continue # this is a directory, don't process it.
# get mask
    mask_name = mask_filename.split(".")[0]
    print("## " + mask_name)
    mask_img = create_mask_from_images([neurosynth_mask_folder + mask_filename],threshold=0)

    run_desc = discriminability_version_id + mask_name
    #get the results
    summary_results = get_all_subjs_discriminability_masked(
        subj_list, run_desc,ml_data_folderpath=ml_data_folderpath,
        subject_discrim_args = 
        {'train_test_markers_filepath':train_test_markers_filepath, 
         'brain_data_filepath':brain_data_filepath, 
         'resp_trans_func': trialtype_resp_trans_func,
         'mask':mask_img})
    
    summary_results_list[mask_name] = summary_results
    
harvox_mask_folder = ml_data_folderpath + "/masks/response_inhibition_related/harvardoxford/"
harvox_mask_name_list = os.listdir(harvox_mask_folder)
for mask_filename in harvox_mask_name_list:
# get mask
    mask_name = mask_filename.split(".")[0]
    print("## " + mask_name)
    mask_img = create_mask_from_images(harvox_mask_folder + mask_filename,threshold=20)

    run_desc = discriminability_version_id + mask_name
    #get the results
    summary_results = get_all_subjs_discriminability_masked(
        subj_list, run_desc,ml_data_folderpath=ml_data_folderpath,
        subject_discrim_args = 
        {'train_test_markers_filepath':train_test_markers_filepath, 
         'brain_data_filepath':brain_data_filepath, 
         'resp_trans_func': trialtype_resp_trans_func,
         'mask':mask_img})
    
    summary_results_list[mask_name] = summary_results
    
    
    
    
with open(
    ml_data_folderpath + "/discriminability_by_mask_" + 
    discriminability_version_id + ".pkl", 'wb') as handle:
    pickle.dump(summary_results_list,handle)


    