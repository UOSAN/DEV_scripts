import sys
import os
import pandas as pd

sys.path.append(os.path.abspath("../../ml/"))

from apply_loocv_and_save import *
from dev_wtp_io_utils import *
import gc
import nibabel as nib

from os import path



import pickle
from IPython.core.display import display, HTML, Markdown
from nilearn import plotting
from nilearn.masking import compute_brain_mask
import nltools as nlt


from ml_tools import *

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

def sr_regressor_trans_func(X):
#         print(X.columns)
#         print(X[self_report_regression_var])
    return(X[self_report_regression_var])

def decoderConstructor(*args, **kwargs):
    return(DecoderRegressor(scoring='neg_mean_absolute_error',verbose=0, *args, **kwargs))

    

harvox_folderpath = ml_data_folderpath + "/masks/response_inhibition_related/harvardoxford/"
neurosynth_folderpath = ml_data_folderpath + "/masks/response_inhibition_related/"

mask_list = pd.concat([get_mask_df(harvox_folderpath,30),
          get_mask_df(neurosynth_folderpath,0)])


#whole-brain

for self_report_regression_var in ['RTFS_factor_1', 'RTFS_factor_2', 'RTFS_f1_minus_f2']:
    regression_output_folderpath = ml_data_folderpath + "/SST/regress_sr_" + self_report_regression_var
    if os.path.exists(regression_output_folderpath)==False:
        os.mkdir(regression_output_folderpath)
    for source_dataset_name in [
        'post_stop_cg_spatially_concatenated',
        'post_failed_stop_cg_w_supplementary',
        'post_correct_stop_cg_w_supplementary'
    ]:
        source_output_folderpath = regression_output_folderpath + "/" + source_dataset_name
        if os.path.exists(source_output_folderpath)==False:
            os.mkdir(source_output_folderpath)
#         for mlr_i, mlr in mask_list.iterrows():
#             print(mlr['filename'])
        results_filepath=(
            source_output_folderpath + 
            "/regress_sr_no_zscore" + self_report_regression_var + "_84subs_" + 
        "wholebrain" + ".pkl"
        )
        print(results_filepath)
        do_complete_sr_regression_analysis_for_mask(
#             mask_filepath = mlr['filepath'],
#             mask_threshold = mlr['threshold'],
                results_filepath = results_filepath,
                apply_loocv_and_save_kwargs = 
                {'response_transform_func':sr_regressor_trans_func,
                    'decoderConstructor' : decoderConstructor,
                    
                    'brain_data_filepath' : ml_data_folderpath + '/SST/Brain_Data_posterror_conditions_84subs_' + source_dataset_name + '.pkl',
                    'train_test_markers_filepath' : train_test_markers_filepath
                    }
        )

#masked
        
for self_report_regression_var in ['RTFS_factor_1', 'RTFS_factor_2', 'RTFS_f1_minus_f2']:
    regression_output_folderpath = ml_data_folderpath + "/SST/regress_sr_" + self_report_regression_var
    if os.path.exists(regression_output_folderpath)==False:
        os.mkdir(regression_output_folderpath)
    for source_dataset_name in [
        'post_stop_cg_spatially_concatenated',
        'post_failed_stop_cg_w_supplementary',
        'post_correct_stop_cg_w_supplementary'
    ]:
        source_output_folderpath = regression_output_folderpath + "/" + source_dataset_name
        if os.path.exists(source_output_folderpath)==False:
            os.mkdir(source_output_folderpath)
        for mlr_i, mlr in mask_list.iterrows():
            print(mlr['filename'])
            results_filepath=(
                source_output_folderpath + 
                "/regress_sr_no_zscore_" + self_report_regression_var + "_84subs_" + 
                mlr['name'] + ".pkl"
            )
            print(results_filepath)
            do_complete_sr_regression_analysis_for_mask(
                mask_filepath = mlr['filepath'],
                mask_threshold = mlr['threshold'],
                results_filepath = results_filepath,
                apply_loocv_and_save_kwargs = 
                {'response_transform_func':sr_regressor_trans_func,
                    'decoderConstructor' : decoderConstructor,
                    
                    'brain_data_filepath' : ml_data_folderpath + '/SST/Brain_Data_posterror_conditions_84subs_' + source_dataset_name + '.pkl',
                    'train_test_markers_filepath' : train_test_markers_filepath
                    }
            )
            