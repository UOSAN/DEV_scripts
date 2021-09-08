from apply_loocv_and_save import *


data_path = '/gpfs/projects/sanlab/bsmith16/data/'



# Split files
dataset_name = 'ns_2s_split_6'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)

dataset_name = 'ns_2s_split_8'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)

dataset_name = 'ns_2s_split_10'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)

dataset_name = 'ns_2s_split_12'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)
