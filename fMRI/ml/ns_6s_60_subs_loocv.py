from apply_loocv_and_save import *
#     def apply_loocv_and_save(
#     brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
#     train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
#     results_filepath="",
#     subjs_to_use = None #set this to get a subset, otherwise use all of them.
# ):
    
apply_loocv_and_save(
    brain_data_filepath = '../data/Brain_Data_ns_6s_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    results_filepath="../data/cv_train_test_ns_6s60subjs_sets_outer_n_loocv.pkl"
)
