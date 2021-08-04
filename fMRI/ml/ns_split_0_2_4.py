from apply_loocv_and_save import *


apply_loocv_and_save(
    brain_data_filepath = '../data/Brain_Data_ns_w_hrf_60subs_split_0.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    results_filepath="../data/cv_train_test_ns_w_hrf_60subjs_split_0.pkl"
)

apply_loocv_and_save(
    brain_data_filepath = '../data/Brain_Data_ns_w_hrf_60subs_split_2.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    results_filepath="../data/cv_train_test_ns_w_hrf_60subjs_split_2.pkl"
)

apply_loocv_and_save(
    brain_data_filepath = '../data/Brain_Data_ns_w_hrf_60subs_split_4.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    results_filepath="../data/cv_train_test_ns_w_hrf_60subjs_split_4.pkl"
)
