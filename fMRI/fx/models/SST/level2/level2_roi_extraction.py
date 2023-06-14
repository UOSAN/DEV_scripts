import nilearn as nil
import pandas as pd
import numpy as np
from direct_regression.get_all_series import get_beta_img, mask_3d_subject_image, signature_weight_3d_subject_image


def load_rois(mask_df):
    raw_mask_list = []
    for m_i, m_set in mask_df.iterrows():
        print(m_set['mask_label'])
        print('producing the vector for this mask/series...')
        #get the mask
        mask_raw = nil.image.load_img(m_set['mask_path'])
        raw_mask_list = raw_mask_list + [mask_raw]

    return raw_mask_list

def get_roi_data_for_beta(
        subject_id,
        wave,
        spm_l2_path,
        condition,
        beta_name,
          raw_roi_list, roi_df, active_img_cleaned):
    roi_data_for_beta = []
    roi_df = roi_df.copy().reset_index(drop=True)

    for m_i, m_set in roi_df.iterrows():
        print(subject_id + ", " + str(wave) + ", " + condition + ", " + m_set['mask_label'])
        #print('producing the vector for this mask/series...')
        
        #active_mask = nilearn.masking.compute_brain_mask(m_set['mask_path'])
        
        roi_raw = raw_roi_list[m_i]

        if 'image_type' not in m_set.keys():
            #no image type set. need to handle this case first in order to avoid errors.
            active_img_masked = mask_3d_subject_image(roi_raw, active_img_cleaned, bin_threshold=np.max(roi_raw.get_fdata())/1000)
        elif m_set['image_type'] == 'mask':
            #binary threshold has to be not quite zero because, with the dtype transform, 
            # some zeros get rounded up to a very-close-to-zero amount.
            active_img_masked = mask_3d_subject_image(roi_raw, active_img_cleaned, bin_threshold=np.max(roi_raw.get_fdata())/1000)
        elif m_set['image_type'] == 'signature':
            active_img_masked = signature_weight_3d_subject_image(roi_raw, active_img_cleaned)
        else:
            raise ValueError("image type not recognized")
        

        activity_scalar = active_img_masked.mean()
        print("activity scalar is " + str(activity_scalar))
        roi_data_for_beta.append({
            'subject_id': subject_id,#r['subject_id'],
            'wave':wave,# r['wave'],
            'spm_l2_path':spm_l2_path,#r['spm_l2_path'],
            'condition' : condition,
            'beta_name': beta_name,#r[colname],
            'mask_label': m_set['mask_label'],
            'roi_activity': activity_scalar
        })
    return roi_data_for_beta


def get_roi_data_for_multirun_l2_betas(beta_list,condition_list,mask_df,spatial_mean_center=False,
                                       collapse_runs=False):
    ###
    #takes a beta list where each entry is one beta image 
    #mean-centers each mask
    #and gets the ROI data for each beta image
    
    
    raw_mask_list = load_rois(mask_df)

    roi_data_all = []

    #iterate through each subject and wave
    for sub_i,sub in enumerate(np.unique(beta_list.subject_id)):
        #and through each condition
        for wave_i,wave in enumerate(np.unique(beta_list.wave)):
            #get the conditions applicable for this subject
            session_betas = beta_list[(beta_list['subject_id']==sub) & (beta_list['wave']==wave)]
            #iterate through each condition
            for condition in set(np.unique(session_betas.beta_description)).intersection(set(condition_list)):
                #get the betas for this condition
                condition_betas = session_betas[session_betas['beta_description']==condition]
                #iterate through each beta
                for i, r in condition_betas.iterrows():
                    #some checks where skipping is necessary
                    if type(r['beta_fname'])==float:
                        if np.isnan(r['beta_fname']):
                            continue
                        #we want an error thrown if somehow it's a float but not nan,
                        # so we handle that case here.
                    if r['beta_fname'] is None:
                        continue
                    
                
                    #get the beta image from which to pull an ROI
                    beta_img_filepath = r['spm_l2_path'] + r['beta_fname']
                    active_img_cleaned = get_beta_img(beta_img_filepath)
                    if active_img_cleaned is None:
                        continue

                    print("img mean is " + str(np.mean(active_img_cleaned.get_fdata()[np.isnan(active_img_cleaned.get_fdata())==False])))

                    if spatial_mean_center:
                        #mean center the nifti image
                        raise NotImplementedError("spatial mean centering not implemented")
                        active_img_cleaned = active_img_cleaned - active_img_cleaned.mean()


                        #active_img_cleaned = active_img_cleaned - active_img_cleaned.mean()

                    #for each mask
                    roi_data_from_masks = get_roi_data_for_beta(
                            r['subject_id'],
                            r['wave'],
                            r['spm_l2_path'],
                            condition,
                            r['beta_fname'],
                            raw_mask_list, mask_df, active_img_cleaned)
                    roi_data_from_masks_df = pd.DataFrame(roi_data_from_masks)
                    roi_data_from_masks_df['run'] = r['task_run']
                    roi_data_all.append(roi_data_from_masks_df)
                    
    roi_data_all_df = pd.concat(roi_data_all)

    if collapse_runs:
        roi_data_all_df = collapse_runs(roi_data_all_df)

    return roi_data_all_df



def get_roi_data_for_l2_betas(beta_list, condition_list,roi_df):
    col_function=lambda img_name: "beta_" + img_name + "_fname"
    #iterate through each mask
    
    raw_roi_list = load_rois(roi_df)



    #now iterate through each beta image
    #for each beta type
    roi_data_all = []
    for condition in condition_list:
        print(condition)
        colname = col_function(condition)
        
        #iterate through each image, if it exists, and pull the ROI
        for i, r in beta_list.iterrows():
            #print(r['subject_id'] + ", " + str(r['wave']))xx
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

            roi_data_all.append(
                get_roi_data_for_beta(
                    r['subject_id'],
                    r['wave'],
                    r['spm_l2_path'],
                    condition,
                    r[colname],
                    raw_roi_list, roi_df, active_img_cleaned)
            )

    roi_data_df = pd.DataFrame(roi_data_all)
    return roi_data_df
