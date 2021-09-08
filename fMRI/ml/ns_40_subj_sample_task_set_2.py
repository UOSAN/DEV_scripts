from apply_loocv_and_save import *


data_path = '/gpfs/projects/sanlab/bsmith16/data/'


# Fingerpress
dataset_name = 'ns_w_hrf_from_spm_before_fingerpress'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)

