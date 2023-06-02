import nilearn as nil
import pandas as pd
import numpy as np
from direct_regression.get_all_series import get_beta_img, mask_3d_subject_image

def get_roi_data_for_l2_betas(beta_list, condition_list,mask_df):
    col_function=lambda img_name: "beta_" + img_name + "_fname"
    #iterate through each mask
    raw_mask_list = []
    for m_i, m_set in mask_df.iterrows():
        print(m_set['mask_label'])
        print('producing the vector for this mask/series...')
        #get the mask
        mask_raw = nil.image.load_img(m_set['mask_path'])
        raw_mask_list = raw_mask_list + [mask_raw]




    #now iterate through each beta image
    #for each beta type
    roi_data_all = []
    for condition in condition_list:
        colname = col_function(condition)
        
        #iterate through each image, if it exists, and pull the ROI
        for i, r in beta_list.iterrows():
            #print(r.index)
            #some checks where skipping is necessary
            if colname not in beta_list.columns:
                continue
            if type(r[colname])==float:
                if np.isnan(r[colname]):
                    continue
                #we want an error thrown if somehow it's a float but not nan,
                # so we handle that case here.
            if r[colname] is None:
                continue
            
        
            #get the beta image from which to pull an ROI
            beta_img_filepath = r['spm_l2_path'] + r[colname]
            active_img_cleaned = get_beta_img(beta_img_filepath)
            if active_img_cleaned is None:
                continue

            #for each mask

            for m_i, m_set in mask_df.iterrows():
                print(colname + ", " + condition + ", " + m_set['mask_label'])
                #print('producing the vector for this mask/series...')
                
                #active_mask = nilearn.masking.compute_brain_mask(m_set['mask_path'])
                mask_raw = raw_mask_list[m_i]

                #binary threshold has to be not quite zero because, with the dtype transform, 
                # some zeros get rounded up to a very-close-to-zero amount.
                active_img_masked = mask_3d_subject_image(mask_raw, active_img_cleaned, bin_threshold=np.max(mask_raw.get_fdata())/1000)

                activity_scalar = active_img_masked.mean()
                roi_data_all.append({
                    'subject_id': r['subject_id'],
                    'wave': r['wave'],
                    'spm_l2_path': r['spm_l2_path'],
                    'condition' : condition,
                    'beta_name': r[colname],
                    'mask_label': m_set['mask_label'],
                    'roi_activity': activity_scalar
                })

    roi_data_df = pd.DataFrame(roi_data_all)
    return roi_data_df
