import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m","--maskpath",
                    help="the mask path (use double quotes if necessary)",
                    type=str)

parser.add_argument("-t","--maskthreshold",
                    help="the mask threshold",
                    type=str)

parser.add_argument("-r","--regressionvar",
                    help="the variable to regress on",
                    type=str)

parser.add_argument("-s","--sourcepath",
                    help="path of the source data",
                    type=str)

parser.add_argument("-o","--outpath",
                    help="file path to save the output",
                    type=str)

args = parser.parse_args()

print("arg pass maskpath is: " + args.maskpath)
print("regression_var is: " + args.regressionvar)
print("sourcepath is: " + args.sourcepath)
print("outpath is: " + args.outpath)


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

from analyze_results import *

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



def decoderConstructor(*args, **kwargs):
    return(DecoderRegressor(scoring='neg_mean_absolute_error',verbose=0, *args, **kwargs))

    
def do_complete_sr_regression_analysis_for_mask(
    self_report_regression_var,
    mask_filepath,
    mask_threshold,
    results_filepath,
    source_dataset_relpath
):
    mask_filename = os.path.basename(mask_filepath)
    mask_name = mask_filename.split(".")[0]

    display(Markdown("## " + mask_name))
    mask_img = create_mask_from_images([mask_filepath],threshold=mask_threshold)
    
    dataset_name = 'conditions'
    
    brain_data_filepath = ml_data_folderpath + source_dataset_relpath
    #brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_conditions_43subs_correct_cond.pkl'

    def sr_regressor_trans_func(X):
        return(X[self_report_regression_var])
    
    if path.exists(results_filepath) is False:
        apply_loocv_and_save(
            results_filepath = results_filepath,
            brain_data_filepath = brain_data_filepath,
            train_test_markers_filepath = train_test_markers_filepath,
#            subjs_to_use = 20,
            decoderConstructor = decoderConstructor,
            response_transform_func=sr_regressor_trans_func,
            mask=mask_img
        )
    print(results_filepath)
    results=pickle.load(open(results_filepath,'rb'))


    visualize_series_corr(results[2]['y'],results[2]['y_pred'])

    return(results)

# harvox_folderpath = ml_data_folderpath + "/masks/response_inhibition_related/harvardoxford/"
# neurosynth_folderpath = ml_data_folderpath + "/masks/response_inhibition_related/"



# def get_mask_df(mask_folder,mask_threshold):
#     mask_name_list = os.listdir(mask_folder)
#     mask_dict_list = []
#     for mask_filename in mask_name_list:
#         mask_filepath = mask_folder + mask_filename
#         if os.path.isdir(mask_filepath):
#             continue # this is a directory, don't process it.
            
#         mask_dict_list = mask_dict_list + [
#             {'name':mask_filename.split(".")[0],
#                 'filename' : mask_filename,
#              'filepath' : mask_filepath,
#              'threshold': mask_threshold
#             }]
#     return(pd.DataFrame(mask_dict_list))

# mask_list = pd.concat([get_mask_df(harvox_folderpath,30),
#           get_mask_df(neurosynth_folderpath,0)])



# for self_report_regression_var in ['TESQ_E_sum', 'TESQ_E_distraction','TESQ_E_suppression']:
#     regression_output_folderpath = ml_data_folderpath + "/SST/regress_sr_" + self_report_regression_var
#     if os.path.exists(regression_output_folderpath)==False:
#         os.mkdir(regression_output_folderpath)
#     for source_dataset_name in ['correct_go','correct_stop']:
#         source_output_folderpath = regression_output_folderpath + "/" + source_dataset_name
#         if os.path.exists(source_output_folderpath)==False:
#             os.mkdir(source_output_folderpath)
#         for mlr_i, mlr in mask_list.iterrows():
#             print(mlr['filename'])
#             results_filepath=(
#                 source_output_folderpath + 
#                 "/regress_sr_" + self_report_regression_var + "_84subs_" + 
#                 mlr['name'] + ".pkl"
#             )
#             do_complete_sr_regression_analysis_for_mask(
#                 self_report_regression_var = self_report_regression_var,
#                 mask_filepath = mlr['filepath'],
#                 mask_threshold = mlr['threshold'],
#                 results_filepath = results_filepath,
#                 source_dataset_relpath = '/SST/Brain_Data_conditions_84subs_' + source_dataset_name + '_w_supplementary.pkl'
#             )
            

print("arg pass maskpath is: " + args.maskpath)
print("regression_var is: " + args.regressionvar)
print("sourcepath is: " + args.sourcepath)
print("outpath is: " + args.outpath)

do_complete_sr_regression_analysis_for_mask(
    self_report_regression_var = args.regressionvar,
    mask_filepath = args.maskpath,
    mask_threshold = int(args.maskthreshold),
    results_filepath = args.outpath,
    source_dataset_relpath = args.sourcepath#'/SST/Brain_Data_conditions_84subs_' + source_dataset_name + '_w_supplementary.pkl'
)