import os
import nilearn as nil
import pandas as pd
import numpy as np
from direct_regression.get_all_series import get_beta_img, mask_3d_subject_image, mask_4d_subject_image, signature_weight_3d_subject_image

#for backwards compatibility, we expose some functions that work without the class

def get_roi_data_for_beta(
            subject_id,
            wave,
            spm_l2_path,
            condition,
            beta_name,
            raw_roi_list, roi_df, active_img_cleaned):
    return level2_roi_extractor().get_roi_data_for_beta(
            subject_id,
            wave,
            spm_l2_path,
            condition,
            beta_name,
            raw_roi_list, roi_df, active_img_cleaned)

def get_roi_data_for_l2_betas():
    return level2_roi_extractor().get_roi_data_for_l2_betas()

def load_rois(mask_df):
    return level2_roi_extractor().load_rois(mask_df)

def get_roi_data_for_multirun_l2_betas(beta_list,condition_list,mask_df,spatial_mean_center=False,
                                        collapse_runs=False):
    return level2_roi_extractor().get_roi_data_for_multirun_l2_betas(beta_list,condition_list,mask_df,spatial_mean_center=False,
                                        collapse_runs=False)

class level2_roi_extractor:

    # define init
    def __init__(self,center_data=False, scale_data=False):
        self.center_data = center_data
        self.scale_data = scale_data
        self.load_all_images_simultaneously = False
        self.image_standardize = False
        self.brain_mask_path = None


    def load_rois(self, mask_df):
        raw_mask_list = []
        for m_i, m_set in mask_df.iterrows():
            print(m_set['mask_label'])
            print('producing the vector for this mask/series...')
            #get the mask
            mask_raw = nil.image.load_img(m_set['mask_path'])
            raw_mask_list = raw_mask_list + [mask_raw]

        return raw_mask_list
    
    def mask_subject_image(self,roi_raw, active_img_cleaned, bin_threshold):
        if len(active_img_cleaned.shape)==3 or active_img_cleaned.shape[3]==1:
            masked_img = mask_3d_subject_image(roi_raw, active_img_cleaned, bin_threshold)
        elif len(active_img_cleaned.shape)==4:
            masked_img = mask_4d_subject_image(roi_raw, active_img_cleaned, bin_threshold)
        return(masked_img)
    

    def get_roi_data_for_beta(self, 
            subject_id,
            wave,
            spm_l2_path,
            condition,
            beta_name,
            raw_roi_list, roi_df, active_img_cleaned):
        roi_data_for_beta = []
        roi_df = roi_df.copy().reset_index(drop=True)
        #rules for input: 
        # length of active_img_cleaned can be 1 or more
        # subject_id should be a scalar, a string, or an iterable with the same number of images in active_img_cleaned
        assert (len(subject_id)==active_img_cleaned.shape[3] or isinstance(subject_id,str) or (not hasattr(subject_id, "__iter__")))
        # length of beta_name should also be 1 or the same as the number of images in active_img_cleaned
        assert (len(beta_name)==active_img_cleaned.shape[3] or isinstance(beta_name,str) or (not hasattr(beta_name, "__iter__")))
        #if subject_id or wave are iterables, then beta_name should be, too
        if (
            (hasattr(subject_id, "__iter__") and subject_id is not str) or
            (hasattr(wave, "__iter__") and wave is not str)):
            assert (hasattr(beta_name, "__iter__") and beta_name is not str)
        # masks are always independent of the number of images in active_img_cleaned
        
        for m_i, m_set in roi_df.iterrows():
            print(str(subject_id) + ", " + str(wave) + ", " + str(condition) + ", " + m_set['mask_label'])
            
            roi_raw = raw_roi_list[m_i]

            if 'image_type' not in m_set.keys():
                #no image type set. need to handle this case first in order to avoid errors.
                active_img_masked = self.mask_subject_image(roi_raw, active_img_cleaned, bin_threshold=np.max(roi_raw.get_fdata())/1000)
            elif m_set['image_type'] == 'mask':
                #binary threshold has to be not quite zero because, with the dtype transform, 
                # some zeros get rounded up to a very-close-to-zero amount.
                active_img_masked = self.mask_subject_image(roi_raw, active_img_cleaned, bin_threshold=np.max(roi_raw.get_fdata())/1000)
            elif m_set['image_type'] == 'signature':
                #handles a bit differently; for signatures we don't set a binary threshold; the images are simply multiplied together.
                active_img_masked = signature_weight_3d_subject_image(roi_raw, active_img_cleaned)
            else:
                raise ValueError("image type not recognized")
            
            if len(active_img_masked.shape)==1:
                activity_scalar = active_img_masked.mean()
            elif len(active_img_masked.shape)==2:
                #get row means of the masked image
                activity_scalar = active_img_masked.mean(axis=1)


            print("activity scalar is " + str(activity_scalar))
            roi_data_for_beta.append(pd.DataFrame({
                'subject_id': subject_id,#r['subject_id'],
                'wave':wave,# r['wave'],
                'spm_l2_path':spm_l2_path,#r['spm_l2_path'],
                'condition' : condition,
                'beta_name': beta_name,#r[colname],
                'mask_label': m_set['mask_label'],
                'roi_activity': activity_scalar
            }))
        return roi_data_for_beta



    def get_roi_data_for_multirun_l2_betas(self, beta_list,condition_list,mask_df,spatial_mean_center=False,
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
    


    def get_roi_data_for_l2_contrasts(self, beta_list, condition_list,roi_df):
        col_function=lambda img_name: "contrast_" + img_name + "_fname"
        #iterate through each mask
        return(self.get_roi_data_for_l2(beta_list,condition_list,roi_df,col_function))

    def subtract_mean(self, image_series):
        img_mask = self.brain_mask_path
                # Get a mean image within the roi
        mean_image = nil.image.math_img("np.mean(img1 * img2, axis=-1)",
                                img1=image_series, img2=img_mask)
        
        # duplicate the mean image to have the same shape as image_series
        mean_image = nil.image.new_img_like(image_series, 
                                        np.repeat(mean_image.get_fdata()[..., np.newaxis], 
                                                image_series.shape[-1], axis=-1))

        # Subtract the mean from each image
        standardized_images = nil.image.math_img('(img1 - img2)', img1=image_series, img2=mean_image)
        return(standardized_images)
    
    def get_image_series(self, beta_list,colname):
            
        beta_filepaths = [r['spm_l2_path'] + r[colname] for i, r in beta_list.iterrows()]
        #strip out the filepaths that don't exist
        filepath_exists = [os.path.exists(b) for b in beta_filepaths]
        beta_list_exists = beta_list[filepath_exists].reset_index(drop=True,inplace=False)
        del beta_list

        #get just the beta_filepaths that exist by indexing beta_filepaths with the boolean array
        beta_filepath_exists = [beta_filepaths[i] for i in range(len(beta_filepaths)) if filepath_exists[i]]

        print("loading " + str(len(beta_filepath_exists)) + "images...")
        image_series = nil.image.load_img(beta_filepath_exists)
        print("...loaded.")
        return(image_series,beta_list_exists)


    def get_roi_data_across_all_betas(self,beta_list: pd.DataFrame, condition,col_function, raw_roi_list, roi_df):

        colname = col_function(condition)
        image_series,beta_list_exists = self.get_image_series(beta_list,colname)

        #clean the image
        image_series_cleaned = nil.image.clean_img(image_series,detrend=self.center_data ,standardize=self.scale_data)

        if self.image_standardize:
            #get the f
            image_series_cleaned = nil.image.standardize(image_series_cleaned)

        #image_series_cleaned.to_filename('cleaned_img.nii.gz')
        # img_cleaned_fdata = image_series_cleaned.get_fdata()
        # #get the mean over the image series
        # img_mean = nil.image.mean_img(image_series_cleaned)
        # #plot
        # nil.plotting.plot_img(img_mean)

        roi_data_for_beta = self.get_roi_data_for_beta(
                    beta_list_exists['subject_id'].tolist(),
                    beta_list_exists['wave'].tolist(),
                    beta_list_exists['spm_l2_path'].tolist(),
                    condition,
                    beta_list_exists[colname].tolist(),
                    raw_roi_list, roi_df, image_series_cleaned)
        
        roi_data_all = roi_data_for_beta

        return(roi_data_all)




    def get_roi_data_for_roi_col(self,beta_list, condition,col_function, raw_roi_list, roi_df):

        colname = col_function(condition)

        roi_data_all = []

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

            if self.center_data or self.scale_data:
                raise NotImplementedError("centering and scaling not implemented")

            if active_img_cleaned is None:
                continue

            #for each mask
            roi_data_for_beta = self.get_roi_data_for_beta(
                    r['subject_id'],
                    r['wave'],
                    r['spm_l2_path'],
                    condition,
                    r[colname],
                    raw_roi_list, roi_df, active_img_cleaned)
            
            roi_data_all.append(pd.DataFrame(roi_data_for_beta))
            
        return(roi_data_all)
    
    def get_roi_data_for_l2(self, beta_list,condition_list,roi_df,col_function):
        raw_roi_list = self.load_rois(roi_df)
        #now iterate through each beta image
        #for each beta type
        roi_data_all = []
        for condition in condition_list:
            print(condition)
            
            if self.load_all_images_simultaneously:
                roi_data = self.get_roi_data_across_all_betas(beta_list, condition,col_function, raw_roi_list, roi_df)
            else:
                roi_data = self.get_roi_data_for_roi_col(beta_list, condition,col_function, raw_roi_list)
            roi_data_all = roi_data_all + roi_data
            

        roi_data_df = pd.concat(roi_data_all)
        return roi_data_df


    def get_roi_data_for_l2_betas(self, beta_list, condition_list,roi_df):
        col_function=lambda img_name: "beta_" + img_name + "_fname"
        #iterate through each mask
        return(self.get_roi_data_for_l2(beta_list,condition_list,roi_df,col_function))

