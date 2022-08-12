from apply_loocv_and_save import *

import gc
import nibabel as nib


def transform_normalize(X):
    wsr_means = pd.DataFrame(X.groupby(['wave','subject','run']).response.mean()).reset_index()
    wsr_means = wsr_means.rename(columns={'response':'response_mean'})
    wsr_sds = pd.DataFrame(X.groupby(['wave','subject','run']).response.std()).reset_index()
    wsr_sds = wsr_sds.rename(columns={'response':'response_sd'})
    
    X_augmented = X[['run','wave','subject','response']].copy().merge(wsr_means).merge(wsr_sds)
    response_norm = (X_augmented.response-X_augmented.response_mean)/X_augmented.response_sd
    #now we need to group by 
    return(response_norm)

#now we run these, but with the response_norm variable instead


data_path = '/gpfs/projects/sanlab/bsmith16/data/'

# HRF 2s
dataset_name = 'ns_w_hrf_from_spm'
#normal

## Whole-brain
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40
)


## PFC only
mask_nifti = nib.load(data_path + 'prefrontal_cortex.nii.gz')


apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_mask_pfc.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40,
    mask = mask_nifti
)


#transformed

## Whole-brain
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_transformed.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    response_transform_func = transform_normalize,
    subjs_to_use = 40
)


## PFC only
mask_nifti = nib.load(data_path + 'prefrontal_cortex.nii.gz')


apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_mask_pfc_transformed.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40,
    response_transform_func = transform_normalize,
    mask = mask_nifti
)
