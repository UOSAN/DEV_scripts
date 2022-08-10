from apply_loocv_and_save import *
import gc
import nibabel as nib

def transform_binary(X):
    wsr_means = pd.DataFrame(X.groupby(['wave','subject','run']).response.mean()).reset_index()
    wsr_means = wsr_means.rename(columns={'response':'response_mean'})
    X_augmented = X[['run','wave','subject','response']].copy().merge(wsr_means)
    response_norm = (X_augmented.response>X_augmented.response_mean).astype(float)
    return(response_norm)
    
data_path = '/gpfs/projects/sanlab/bsmith16/data/'
mask_nifti = nib.load(data_path + 'prefrontal_cortex.nii.gz')

#2s HRF
# dataset_name = 'ns_w_hrf_from_spm'
# apply_loocv_and_save(
#     results_filepath=data_path + "train_test_simple_results_" + dataset_name + "_40subs_bintransform.pkl",
#     brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
#     train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
#     response_transform_func = transform_binary,
#     subjs_to_use = 40)

# apply_loocv_and_save(
#     results_filepath=data_path + "train_test_simple_results_" + dataset_name + "_40subs_pfc_bintransform.pkl",
#     brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
#     train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
#     response_transform_func = transform_binary,
#     subjs_to_use = 40,
#     mask = mask_nifti)

# # Split files
# for split in ['0','2','4','6','8','10','12']:
#     dataset_name = 'ns_2s_split_' + split
#     apply_loocv_and_save(
#         results_filepath=data_path + "train_test_simple_results_" + dataset_name + "_40subs_bintransform.pkl",
#         brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
#         train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
#         response_transform_func = transform_binary,
#         subjs_to_use = 40)

# Fingerpress
dataset_name = 'ns_w_hrf_from_spm_before_fingerpress'

apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_bintransform.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    response_transform_func = transform_binary,
    subjs_to_use = 40)


# apply_loocv_and_save(
#     results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_pfc_bintransform.pkl",
#     brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
#     train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
#     response_transform_func = transform_binary,
#     subjs_to_use = 40,
#     mask = mask_nifti
# )


# 4s
# dataset_name = 'ns_4s_w_hrf_from_spm'

# #### Whole-brain
# apply_loocv_and_save(
#     results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_bintransform.pkl",
#     brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
#     train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
#     response_transform_func = transform_binary,
#     subjs_to_use = 40)


#### PFC only
# apply_loocv_and_save(
#     results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_mask_pfc_bintransform.pkl",
#     brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
#     train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
#     subjs_to_use = 40,
#     response_transform_func = transform_binary,
#     mask = mask_nifti)



