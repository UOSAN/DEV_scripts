import glob
import pandas as pd
import re
import nilearn as nil
from nilearn import *
from nilearn import image
from os.path import basename
import numpy as np
import yaml
from yaml.loader import SafeLoader
from socket import gethostname

# get all series
# get masks
# iterate through series
# iterate through masks
# produce the vector for this mask/series

# for each trial [CS, CG, FS, FG], identify the moment the subject learns the class of the trial;
# this may be slightly different for Go and Stop trials. For Stop trials it is simply the moment of the tone;
# for Go trials it's harder to specify.
# for each TRIAL, you will end up with a data table with columns (a) time from trial class reveal to image; (b) separate columns for measurement of each ROI
# these can be concatenated across trials, runs, and subjects
# then create n_{ROI}*n_{trial classes} graphs of samples, where x is the time from trial class reveal to image, and y is the measurement. plot a lowess curve.
# potentially overlay the lowess curves for each trial type so that the response within each ROI can be easily compared.


def get_roi_data(nii_raw_files, mask_df):
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

    return(roi_data)

# for each trial [CS, CG, FS, FG], identify the moment the subject learns the class of the trial;
# this may be slightly different for Go and Stop trials. For Stop trials it is simply the moment of the tone;
# for Go trials it's harder to specify.
def get_moment_trial_type_revealed(trial_type, ssdr,first_tone):
    trial_type = trial_type.tolist()
    ssdr = ssdr.tolist()
    expected_tone_time = pd.Series([0.]*len(ssdr))
    expected_tone_time[0]=first_tone
    expected_tone_time[1]=first_tone

    for i in range(2,len(expected_tone_time)):
         #these are in increments of 2 because every second event is a cue
         #previous trial was a stop
        if trial_type[i]=="Stop":
            expected_tone_time[i] = ssdr[i]
        else:
            expected_tone_time[i] = expected_tone_time[i-1]
    #print(expected_tone_time)
    return(expected_tone_time)

# but might be the expected time of the onset, which would be the _previous_ stop trial.
#create expected tone table
def get_behavioral_data_with_moment_trial_type_revealed(sst_all_behavioral_data):
    expected_tone_table = sst_all_behavioral_data.groupby(['subid', 'waveid','runid']).apply(
        lambda sabd_set: get_moment_trial_type_revealed(sabd_set['go_no_go_condition_label'], sabd_set['SSD_recorded'],first_tone=2)
    )
    expected_tone_table2=expected_tone_table.reset_index()
    expected_tone_table2.rename(columns={0:'class_type_reveal'},inplace=True)
    expected_tone_table2.loc[:,'trial_n']=expected_tone_table2.level_3+1
    expected_tone_table2.drop('level_3',axis=1,inplace=True)

    sst_all_behavioral_data = sst_all_behavioral_data.merge(expected_tone_table2,
    left_on=['subid','waveid','runid','trial_n'],
    right_on =['subid','waveid','runid','trial_n'],
    how='left'
        
        )
    return(sst_all_behavioral_data)

        

def get_all_subj_df(roi_data, sst_all_behavioral_data):
    # (is there a way to do this vectorized over ALL the data,
    # or is it more sensible to loop through subjects/runs to do it?
    # tend to think looping through subjects makes more sense.)
    all_subj_df_list = [] 
    for s in roi_data.keys():
        print(s)
        for wave in roi_data[s].keys():
            run_length = roi_data[s][wave].shape[0]
            print(s +', ' + wave + ':' + str(run_length), sep="; ")
            rt_time_list = [x*2.0 for x in range(run_length)]
            #now we have a list of the the RTs
            #we have actual data at each data point
            #we need to get the RTs related to each particular trial.
            run_behavioral_data = sst_all_behavioral_data[(sst_all_behavioral_data.subid==s) & (sst_all_behavioral_data.waveid==int(wave))]

            run_trial_df_list = []
            for i, trial in run_behavioral_data.iterrows():
                #print(i)
                t_class_type_reveal_onset = trial['class_type_reveal_onset']
                #print(trial[['trial_n','class_type_reveal_onset']])
                #grab the set of TR times that are relevant based on its
                

                trial_rt_timing_all = pd.DataFrame({'tr':rt_time_list,'offset':[(tr - t_class_type_reveal_onset) for tr in rt_time_list]})
                trs_to_use_for_trial = ((trial_rt_timing_all.offset>-10) & (trial_rt_timing_all.offset<20))
                trial_rt_timing_inscope = trial_rt_timing_all.loc[trs_to_use_for_trial]

                #and we will also want to grab the actual data we already extracted...
                trial_roi_data = pd.merge(trial_rt_timing_inscope,roi_data[s][wave],how='left',
                left_index=True,right_index=True
                )
                trial_roi_data['t_class_type_reveal_onset']=t_class_type_reveal_onset
                trial_roi_data['subid']=s
                trial_roi_data['wave']=wave
                trial_roi_data['go_no_go_condition_label']=trial[['go_no_go_condition_label']][0]
                trial_roi_data['condition']=trial[['condition']][0]
                trial_roi_data['trial_n']=trial[['trial_n']][0]
                trial_roi_data['trial_n']=trial[['trial_n']][0]
                
                run_trial_df_list.append(trial_roi_data)
                #cool. now what? 

            run_trial_df = pd.concat(run_trial_df_list)
            run_trial_df.reset_index(drop=True,inplace=True)

            all_subj_df_list.append(run_trial_df)
    all_subj_df = pd.concat(all_subj_df_list)

    return(all_subj_df)
        



