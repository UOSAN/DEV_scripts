from apply_loocv_and_save import *


data_path = '/gpfs/projects/sanlab/bsmith16/data/'
# HRF 2s
dataset_name = 'ns_w_hrf_from_spm'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)



# No HRF 2s
dataset_name = 'ns_no_hrf_from_spm'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)


# No HRF 6s
dataset_name = 'ns_6s_no_hrf_from_spm'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + 'train_test_markers_20210601T183243.csv',
    subjs_to_use = 40
)

# Fingerpress
dataset_name = 'ns_w_hrf_from_spm_at_fingerpress'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)


# Split files
dataset_name = 'ns_2s_split_0'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)

dataset_name = 'ns_2s_split_2'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)

dataset_name = 'ns_2s_split_4'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)
