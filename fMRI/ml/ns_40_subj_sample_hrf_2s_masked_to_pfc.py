from apply_loocv_and_save import *
import gc
import nibabel as nib




data_path = '/gpfs/projects/sanlab/bsmith16/data/'

mask_nifti = nib.load(data_path + 'prefrontal_cortex.nii.gz')

# HRF 2s
dataset_name = 'ns_w_hrf_from_spm'
apply_loocv_and_save(
    results_filepath=data_path + "train_test_results_" + dataset_name + "_40subs_mask_pfc.pkl",
    brain_data_filepath = data_path + 'Brain_Data_' + dataset_name + '_60subs.pkl',
    train_test_markers_filepath = data_path + "train_test_markers_20210601T183243.csv",
    subjs_to_use = 40,
    mask = mask_nifti
)


