

def get_roi_data(nii_raw_files, TR):
    roi_data = {}

    for nii in nii_raw_files:
        series_filename = basename(nii)
        match_data = re.match('.*(DEV\d*)_ses-wave(\d+)*',series_filename)
        dev_name = match_data[1]
        dev_wave = match_data[2]

        #print(basename(nii))
        print(dev_name + ", " + dev_wave)

        active_img = image.load_img(nii)
        active_img_cleaned = nil.image.clean_img(active_img)
        del(active_img)
        
        #create a template data frame to populate with the ROI data, for this run
        run_len = active_img_cleaned.shape[3]
        if dev_name not in roi_data.keys():
            roi_data[dev_name]={}
        
        run_df = pd.DataFrame(index=range(0,run_len))
        #run_df = pd.DataFrame({'image_id':range(0,run_len)})
        #run_df['TR_onset']=run_df.image_id*TR


        
        for m_i, m_set in mask_df.iterrows():
            print(m_set['mask_label'])
            print('producing the vector for this mask/series...')
            
            #active_mask = nilearn.masking.compute_brain_mask(m_set['mask_path'])
            mask_raw = nil.image.load_img(m_set['mask_path'])
            mask_in_subj_space = nil.image.resample_img(mask_raw, target_affine=active_img_cleaned.affine,target_shape = active_img_cleaned.slicer[:,:,:,0].shape)
            mask_binarized = nil.image.binarize_img(mask_in_subj_space,threshold=50)
            active_img_masked = nil.masking.apply_mask(active_img_cleaned, mask_binarized)
            activity_vector = active_img_masked.mean(axis=1)
            run_df[m_set['mask_label']]=activity_vector
            print("created an activity vector for this mask with the following length: " + str(len(activity_vector)))
            #
            #nil.plotting.plot_img(mask_applied)
            #nilearn.plotting.view_img(active_mask)
        #now we've gone through all the masks for this run, add the run_df to the dict dict
        roi_data[dev_name][dev_wave] = run_df



        

        

