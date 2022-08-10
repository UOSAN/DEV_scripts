import gc
import nibabel as nib

mask_nifti = nib.load('../data/prefrontal_cortex.nii.gz')

########################################################################
##ns_6s_60_subs_loocv-respnorm.py

# from apply_loocv_and_save import *

# def transform_normalize(X):
#     wsr_means = pd.DataFrame(X.groupby(['wave','subject','run']).response.mean()).reset_index()
#     wsr_means = wsr_means.rename(columns={'response':'response_mean'})
#     wsr_sds = pd.DataFrame(X.groupby(['wave','subject','run']).response.std()).reset_index()
#     wsr_sds = wsr_sds.rename(columns={'response':'response_sd'})
    
#     X_augmented = X[['run','wave','subject','response']].copy().merge(wsr_means).merge(wsr_sds)
#     response_norm = (X_augmented.response-X_augmented.response_mean)/X_augmented.response_sd
#     #now we need to group by 
#     return(response_norm)

    
# apply_loocv_and_save(
#     brain_data_filepath = '../data/Brain_Data_ns_6s_60subs.pkl',
#     train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
#     results_filepath="../data/cv_train_test_ns_6s60subjs_sets_pfc_outer_n_loocv_respnorm.pkl",
#     response_transform_func = transform_normalize,
#     mask = mask_nifti
# )

# gc.collect()

########################################################################
##ns_6s_60_subs_loocv_mean_dichot.py

import pickle
from apply_dichotomized_prediction_loocv_and_save import *
#     def apply_loocv_and_save(
#     brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
#     train_test_maarkers_filepath = "../data/train_test_markers_20210601T183243.csv",
#     results_filepath="",
#     subjs_to_use = None #set this to get a subset, otherwise use all of them.
# ):
    
apply_dichotomized_prediction_loocv_and_save(
    brain_data_filepath = '../data/Brain_Data_ns_6s_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    results_filepath="../data/cv_train_test_ns_6s60subjs_sets_pfc_outer_n_loocv_dichotomized.pkl",
    mask = mask_nifti
)

gc.collect()

########################################################################
## ns_6s_60_subs_loocv


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
    results_filepath="../data/cv_train_test_ns_6s60subjs_sets_pfc_outer_n_loocv.pkl",
    mask = mask_nifti
)

gc.collect()

########################################################################
### ns_w_hrf_60_subs_loocv.py

from apply_loocv_and_save import *
#     def apply_loocv_and_save(
#     brain_data_filepath = '../data/Brain_Data_2sns_60subs.pkl',
#     train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
#     results_filepath="",
#     subjs_to_use = None #set this to get a subset, otherwise use all of them.
# ):
    
apply_loocv_and_save(
    brain_data_filepath = '../data/Brain_Data_ns_w_hrf_60subs.pkl',
    train_test_markers_filepath = "../data/train_test_markers_20210601T183243.csv",
    results_filepath="../data/cv_train_test_ns_w_hrf_60subjs_sets_pfc_outer_n_loocv.pkl",
    mask = mask_nifti
)

gc.collect()