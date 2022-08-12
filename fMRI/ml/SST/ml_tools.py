import sys
import os
import pandas as pd

import pickle
from IPython.core.display import display, HTML, Markdown

sys.path.append(os.path.abspath("../../ml/"))

from apply_loocv_and_save import *
from dev_wtp_io_utils import *
from analyze_results import *
import os
from os import path


def do_complete_sr_regression_analysis_for_mask(
#    self_report_regression_var,
    apply_loocv_and_save_kwargs,
    results_filepath,
    mask_filepath = None,
    mask_threshold = None
    
    
    
):
    if mask_filepath is not None:
        mask_filename = os.path.basename(mask_filepath)
        mask_name = mask_filename.split(".")[0]

        display(Markdown("## " + mask_name))
        mask_img = create_mask_from_images([mask_filepath],threshold=mask_threshold)
    else:
        mask_img = None
    
    dataset_name = 'conditions'
   
    #brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_conditions_43subs_correct_cond.pkl'
    


    if path.exists(results_filepath) is False:
        apply_loocv_and_save(
            mask=mask_img, clean=False,
        decoder_standardize=False,
            results_filepath = results_filepath,
            **apply_loocv_and_save_kwargs
        )
    print(results_filepath)
    results=pickle.load(open(results_filepath,'rb'))

    
    results[2] = remove_selected_outliers(results[2], ['y','y_pred'])
    
    pred_table = results[2]

    outliers = pd.isna(pred_table).any(axis=1)
    pred_vs_actual_no_outliers = pred_table[outliers==False]
    if sum(outliers) > 0:
        print("removed " + str(sum(outliers)) + " outlying predictions or values")

    visualize_series_corr(pred_vs_actual_no_outliers['y'],pred_vs_actual_no_outliers['y_pred'])

    return(results)


def get_mask_df(mask_folder,mask_threshold):
    mask_name_list = os.listdir(mask_folder)
    mask_dict_list = []
    for mask_filename in mask_name_list:
        mask_filepath = mask_folder + mask_filename
        if os.path.isdir(mask_filepath):
            continue # this is a directory, don't process it.
            
        mask_dict_list = mask_dict_list + [
            {'name':mask_filename.split(".")[0],
                'filename' : mask_filename,
             'filepath' : mask_filepath,
             'threshold': mask_threshold
            }]
    return(pd.DataFrame(mask_dict_list))
