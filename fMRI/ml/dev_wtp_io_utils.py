import numpy as np
import pandas as pd
import re
import glob
import os
import scipy.io
import nltools as nlt
import nilearn as nil
import nibabel as nib
import sys
import warnings
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut
from nilearn.decoding import DecoderRegressor,Decoder
from pympler.asizeof import asizeof
import gc #garbage collection
import pickle
from copy import deepcopy


class BehavioralDataNotFoundForBrainDataException(Exception):
    """Behavioral data could not be matched to a subject."""
    pass

#run_object = dev155_wtp_wave1_taskoutput['Data']['run1']
def get_run_event_stage_df(run_object):
    """get a list of individual event stage items.
    Main event stages are bid_prechoice, bid_postchoice, bid_nochoice
    
    """
    event_stage_list = []
    
    for event_i in range(len(run_object['TrialStart'])):
        #summarize and collate data relating to each of the three stages of each event: 
        #(1) onset, (2) pre-choice bid, (3) post-choice bid
        try:
            stage_food={
                'event_id':event_i+1,
                'stage':'food',
                'onset': run_object['FoodOnset'][event_i],
                'end': run_object['FoodOnset'][event_i] + run_object['FoodDuration'][event_i]
            }
            #if we had a choice made
            #if np.isnan(float(run_object['RT'][event_i]))==False:
            if run_object['Resp'][event_i]!='NULL':
                stage_bid_prechoice={
                    'event_id':event_i+1,
                    'stage':'bid_prechoice',
                    'onset': run_object['BidOnset'][event_i],
                    'end': run_object['BidOnset'][event_i] + run_object['RT'][event_i]
                }
                stage_bid_postchoice={
                    'event_id':event_i+1,
                    'stage':'bid_postchoice',
                    'onset': run_object['BidOnset'][event_i] + run_object['RT'][event_i],
                    'end': run_object['BidOnset'][event_i] + run_object['BidDuration'][event_i]
                }
                event_dict_list = [stage_food, stage_bid_prechoice, stage_bid_postchoice]
            else: #if we did NOT have a choice made
                stage_bid_nochoice={
                    'event_id':event_i+1,
                    'stage':'bid_nochoice',
                    'onset': run_object['BidOnset'][event_i],
                    'end': run_object['BidOnset'][event_i] + run_object['BidDuration'][event_i]
                }
                event_dict_list =[stage_food,stage_bid_nochoice]
        except:
            #if we have some processing error, 
            #provide some info about it but still raise the error
            print(run_object)
            print("error is in event " + str(event_i + 1))
            print(run_object['Resp'][event_i])
            raise
        #now collate those three into a list
        
        event_stage_list = event_stage_list + event_dict_list

    event_stage_df = pd.DataFrame(event_stage_list)
    return(event_stage_df)


def get_run_event_df(run_object):
    """
    Given a .mat run object, return the information about each event.
    """
    event_list = [] # list data not pertaining to any particular stage of the event
    for event_i in range(len(run_object['TrialStart'])):
        #now summarize and collate the event data
        event_dict = {
            'event_id': event_i +1,
            'isi_pre':run_object['Jitter'][event_i],
            'onset': run_object['FoodOnset'][event_i],
            'duration': run_object['FoodDuration'][event_i] + run_object['BidDuration'][event_i],
            'food_pic':run_object['FoodPic'][event_i],
            'food_num':run_object['FoodNum'][event_i],
            'cond':run_object['Cond'][event_i],
            'health_cond':run_object['HealthCond'][event_i],
            'liking_cond':run_object['LikingCond'][event_i],
            'liking_rating':run_object['LikingRating'][event_i],
            'response':run_object['Resp'][event_i]
        }
        #only log a 'post-jitter' if there's actually one coming after
        if event_i < (len(run_object['Jitter'])-1):
            event_dict['isi_post'] = run_object['Jitter'][event_i+1]
        else:
            event_dict['isi_post'] = None

        event_dict['end'] = event_dict['onset'] + event_dict['duration']

        event_list = event_list + [event_dict]

    event_df = pd.DataFrame(event_list)
    return(event_df)



def get_comprehensive_run_data_from_mat_dir(mat_dir_path):
    """returns three objects: 
    (1) a run_list (containing a list of runs)
    (2) an event list (containing a list of events)
    (3) an event stage list ( containing a list of event stages divided up by stage)
    """
    run_list = []
    run_event_df_list = []
    run_event_stage_df_list = []

    for subj_mat_dir_pathname in glob.glob(mat_dir_path + 'DEV*'):
        #get the subject folder name
        subj_output_folder_name = os.path.basename(subj_mat_dir_pathname)
        #and get the three digit number that is part of it
        subj_3_digit_number = re.search('DEV(\\d*)',subj_output_folder_name,re.IGNORECASE)[1]

        wave_pathname_list = glob.glob(mat_dir_path + subj_output_folder_name + '/DEV.' + subj_3_digit_number + '.?.mat')

        print('subject ' + subj_3_digit_number,end=', ')
        #iterate through each wave for this subject.
        for wave_pathname in wave_pathname_list:
            #print(wave_pathname)
            subj_regex_code = 'DEV.' + subj_3_digit_number + '.(\\d*).'
            wave_name = re.search(subj_regex_code,os.path.basename(wave_pathname),re.IGNORECASE)[1]

            #we're really just wanting wave 1 right now
            #but let's do all waves because it'll be easier to knock them out now
            #rather than trying to handle them all later.
            #wave1 = glob.glob(mat_dir_path + subj_output_folder_name + '/DEV.' + subj_3_digit_number + '.1.mat')

            #load the wave file for this wave.
            wave_file = scipy.io.loadmat(wave_pathname,simplify_cells=True)

            runs = list(filter(re.compile("run*").match,wave_file['Data'].keys()))


            for run in runs:
                run_object = wave_file['Data'][run]

                #before we do this run, let's check that it is complete
                #if it is abridged a known way, print a specific notification
                if set(run_object.keys())==set(['time']):
                    print("\nSUBJ " + subj_3_digit_number + ", " + wave_name +", " + run)
                    print("no data for this run.")
                    continue
                #if it's missing data but not in any way we expect, print some info and continue
                if len(run_object.keys())!=20:
                    print("\n\nSUBJ " + subj_3_digit_number + ", " + wave_name +", " + run)
                    print("Data for this run is not in the expected format or is missing. Skipping this run.")


                    for k,v in run_object.items():
                        print(k,end=': ')
                        if isinstance(v,np.ndarray):
                            print('array of length ' + str(len(v)))
                        else:
                            print(v)
                        print('')

                    continue

                #create run object
                try:
                    #pick out the keys we want for the run object
                    run_obj_simplified = {
                        ro_key: run_object[ro_key] 
                        if ro_key in run_object.keys() 
                        else None 
                        for ro_key in ['StartTime','EndTime','time']
                    }
                    run_obj_simplified['run'] = run
                    run_obj_simplified['wave'] = wave_name
                    run_obj_simplified['subject'] = 'DEV' + subj_3_digit_number
                    run_list=run_list + [run_obj_simplified]
                except:
                    print(run_object)
                    raise

                #create event list
                run_event_df = get_run_event_df(run_object)
                run_event_df['run'] = run
                run_event_df['wave'] = wave_name
                run_event_df['subject'] = 'DEV' + subj_3_digit_number
                run_event_df_list = run_event_df_list + [run_event_df]


                #create event stage list
                event_stage_df = get_run_event_stage_df(run_object)
                event_stage_df['run'] = run
                event_stage_df['wave'] = wave_name
                event_stage_df['subject'] = 'DEV' + subj_3_digit_number
                run_event_stage_df_list = run_event_stage_df_list + [event_stage_df]


                

    run_event_stage_across_runs_df = pd.concat(run_event_stage_df_list)
    run_event_across_runs_df = pd.concat(run_event_df_list)
    run_list_df = pd.DataFrame(run_list)
    
    #tidy up some stuff
    run_event_across_runs_df.wave = run_event_across_runs_df.wave.astype(int)
    #run_event_across_runs_df.likert_rating = run_event_across_runs_df.likert_rating.astype(int)
    run_event_stage_across_runs_df.wave = run_event_stage_across_runs_df.wave.astype(int)
    run_list_df.wave = run_list_df.wave.astype(int)
    
    return(run_list_df,run_event_across_runs_df,run_event_stage_across_runs_df)


def get_wtp_filepath_for_run(sub_label,wave,run):
    """
    Developed in load_multisubject_raw_data.ipynb. 
    """
    folder_path = (
        "/gpfs/projects/sanlab/shared/DEV/bids_data/derivatives/fmriprep/sub-"+
        sub_label+
        "/ses-wave"+str(wave)+"/func/"
    )
    filename = (
        's6_sub-' + sub_label + '_ses-wave' + str(wave) + 
        '_task-WTP_acq-' + str(run) +'_bold_space-MNI152NLin2009cAsym_preproc.nii'
    )
    
    return(folder_path+filename)

def extract_events_from_nii(subj_raw_data_nii, subj_behav_design):
    """
    Developed in load_multisubject_raw_data.ipynb.  Gets a single subjects' worth of raw data based on a behavioral design.
    """
    slice_series = []
    for event_i, event_r in subj_behav_design.iterrows():
        #print(event_r['onset'])
        #the event tr is the first TR AFTER the onset; so we need to find the point and round-up

        event_tr = (int)(np.ceil(event_r['onset']/2))
        if event_tr<subj_raw_data_nii.shape[3]:
            slice_series = slice_series + [subj_raw_data_nii.slicer[...,event_tr]]
        else:
            raise IndexError("The behavioral design refers to a slice (" + str(event_tr) + ") that is not present in the dataset. This may indicate bad data or a truncated run. The dataset has shape: " + str(subj_raw_data_nii.shape))

        #print(event_tr)

    event_related_nii = nib.funcs.concat_images(slice_series)
    return(event_related_nii)


def get_event_related_Brain_Data_for_all_subs_all_runs_fast(subj_list, wave,all_behav_design):
    """
    Developed in load_multisubject_raw_data.ipynb. Gets raw brain data from raw files and concatenates into a Brain_Data file.
    """
    training_data_list = []
    behavioral_design_list_in_order = []
    for sub_label in subj_list:
        print(sub_label + " (",end='',flush=True)

        #def get_event_related_Brain_Data_for_sub_all_runs(subj_label,wave,all_behav_design):
        #loop through each run
        for run in [1,2,3,4]:
            print(str(run) + " ", end='',flush=True)
            #def get_event_related_Brain_Data_for_sub_run(subj_label,wave,run,all_behav_design):
            #load the raw run file
            raw_filepath = get_wtp_filepath_for_run(sub_label,wave,run)
            #print(raw_filepath)
            subj_raw_data_nii = nib.load(raw_filepath)

            #subset the behavioral data
            subj_behav_design = all_behav_design[
                (all_behav_design.subject==sub_label) &
                (all_behav_design.wave==wave) &
                (all_behav_design.run=='run' + str(run))
            ]
            
            
            #go through the event file and extract the appropriate nii for each event
            try:
                
                event_related_nii = extract_events_from_nii(subj_raw_data_nii, subj_behav_design)
                
                #this is a good place to convert the data from 64 to 32bit. we don't need 64-bit float. might only need 16-bit
                #https://stackoverflow.com/questions/44397617/change-data-type-in-numpy-and-nibabel/45589431
#                 event_related_nii_32b = event_related_nii
#                 event_related_nii_32b
#                 event_related_nii.get_fdata().astype(np.float32)
                training_data_list = training_data_list + [event_related_nii]
                behavioral_design_list_in_order= behavioral_design_list_in_order + [subj_behav_design]
            except IndexError:
                print("For subject " + sub_label + ", run " + str(run) + ", there was a mismatch between behavioral and data. Skipping this run.")
                
        print(")")
                
            
    print("extracted all data. concatenating...",flush=True)
    #concatenate the data from each run into a single file
    all_nii = nib.funcs.concat_images(training_data_list,axis=3)
    del training_data_list #this uses up a LOT of memory. so let's not take more than necessary
    print("...concatenated.",flush=True)
    behavioral_design = pd.concat(behavioral_design_list_in_order)
    behavioral_design.reset_index(inplace=True,drop=True)
    
    print("combining into a Brain_Data file....",flush=True)
    #combine as a Brain_Data file.
    all_bd = nlt.Brain_Data(all_nii)
    all_bd.X = behavioral_design
    print("...done.",flush=True)
    
    return(all_bd)

import numpy as np
import pandas as pd
import re
import glob
import os
import scipy.io
import nltools as nlt
import nilearn as nil
import nibabel as nib
import sys
import warnings
from sklearn.model_selection import KFold,GroupKFold,LeaveOneOut
from nilearn.decoding import DecoderRegressor,Decoder
from pympler.asizeof import asizeof
import gc #garbage collection
import pickle


import nltools as nlt

def Brain_Data_max(x):
    """ Sum over voxels.
    modified from nltools Brain_Data.sum
    you need that
    """

    out = deepcopy(x)
    print(x.shape())
    print(len(x.shape()))
    if len(x.shape()) > 1:
        out.data = np.max(out.data, axis=0)
        out.X = pd.DataFrame()
        out.Y = pd.DataFrame()
    else:
        raise Exception("this function wasn't designed to handle just one image, and there's no point in calling it because it sums over multiple images.")
    return out


def get_pfc_image_filepaths(data_path):
    mask_files=glob.glob(data_path + "masks/prefrontal_cortex/*.nii.gz")
    return(mask_files)

def create_mask_from_images(image_filepath_list,threshold=0):
    mask_set = nlt.Brain_Data(image_filepath_list)
    if len(mask_set.shape())>1:
        mask_aggregate = Brain_Data_max(mask_set).to_nifti()
    else:
        mask_aggregate = mask_set.to_nifti()
    mask_binarized = nil.image.new_img_like(mask_aggregate,(mask_aggregate.get_fdata()>threshold).astype(float))

    return(mask_binarized)

def spatially_concatenate_nifti_series(bd_nifti,zscore = False):
    bd_fdata = bd_nifti.get_fdata()

    img_count = bd_fdata.shape[3]
    bd_array = [bd_fdata[:,:,:,i] for i in range(img_count)]
    if zscore:
        bd_array_zscored = [(e-np.mean(e))/np.std(e) for e in bd_array]
    else:
        bd_array_zscored = bd_array
    bd_reshaped = np.concatenate(bd_array_zscored,axis=0)
    concatenated = nil.image.new_img_like(bd_nifti,bd_reshaped)
    return(concatenated)

def spatially_concatenate_repeated_image(bd_nifti,repetitions,zscore=False):
    bd_fdata = bd_nifti.get_fdata()
    if zscore:
        bd_fdata_zscored = (bd_fdata-np.mean(bd_fdata))/np.std(bd_fdata)
    else:
        bd_fdata_zscored = bd_fdata
    bd_array = [bd_fdata_zscored]*repetitions
    bd_reshaped = np.concatenate(bd_array,axis=0)
    concatenated = nil.image.new_img_like(bd_nifti,bd_reshaped)

    return(concatenated)

def get_Brain_Data_betas_for_sub(
    sub_label,
    behavdesign,
    betaseries_path='/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/WTP/wave1/betaseries/',
    events_in_design = 64,
    mask = None,
    mask_threshold=0.5,
    spatially_concatenate=False
):
    """
    Collect a bunch of beta files for specified subjects based on a behavioral design file
    and return them
    """
    subj_behav_design = behavdesign[[s in sub_label for s in behavdesign.subject]]
    del(behavdesign)
    
    if (len(subj_behav_design)==0):
        raise BehavioralDataNotFoundForBrainDataException(
            "Found no behavioral data for subject " + sub_label + ". Please ensure the data exists - it is probably missing from the source.")
    elif len(subj_behav_design)!=events_in_design:
        raise Exception("For "+sub_label+", expected " +str(events_in_design) + " beta events but found " + str(len(subj_behav_design)))

    
    subject_dir = (
         betaseries_path + 'sub-' + sub_label + '/'
    )
        
    #set path for the betas

    #beta_path_sub049 = os.listdir(subject_dir)

    #iterate through the subjects
    # TO DO
    #iterate through and check all the betas exist
    for betafile in subj_behav_design.beta:
        betafilepath = subject_dir + betafile
        
        #check if file exists
        if os.path.exists(betafilepath):
            print('.',end='')
        else:
            print(betafilepath)
            raise Exception("beta " + betafile + ' does not exist at ' + betafilepath)

    print("...verified that all expected betas exist! Processing...",flush=True,end='')
    
    create_temp_mask = False
    if mask=="beta":
        create_temp_mask= True

    tmp_mask_path = (
        betaseries_path + 
        'temp_mask_get_Brain_Data_betas_for_sub_' + sub_label +
        '.nii'
    )

    #we're always going to use the subject first image as a mask
    #then, if another mask has been passed in to this function, we use the combo of those
    print("retrieving a mask from the first image in the series " + subj_behav_design.beta.iloc[0])

    with warnings.catch_warnings(record=True) as w:
        subj_first_img = nil.image.load_img(subject_dir + subj_behav_design.beta.iloc[0])
        #load the first image to be a mask
        if mask_threshold is None: mask_threshold=0
        subj_mask = nil.masking.compute_brain_mask(subj_first_img,mask_threshold)
        
        if mask!="beta":
            external_mask = nil.image.load_img(mask)

            #now combine the two masks
            external_mask_resampled = nil.image.resample_to_img(external_mask, subj_first_img,interpolation='nearest')
            external_mask_bin = nil.image.math_img("np.round(img,3)>0.1",img=external_mask_resampled)
            final_mask = nil.masking.intersect_masks([subj_mask,external_mask_bin])
            print("...using a combined mask of the first image and the passed in mask",flush=True,end='')
        else:
            final_mask=subj_mask
        #nib.save(external_mask_bin,'/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/betaseries/temp_mask_get_Brain_Data_betas_for_sub_DEV005_bin.nii')
        #nib.save(external_mask_resampled,'/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/betaseries/temp_mask_get_Brain_Data_betas_for_sub_DEV005_resampled.nii')
        nib.save(final_mask,tmp_mask_path)

    for wi in w:
        if wi.message.args[0]!='Resampling binary images with continuous or linear interpolation. This might lead to unexpected results. You might consider using nearest interpolation instead.':
            warnings.warn(wi.message,type(wi))
        else:
            print("During mask creation, received error 'Resampling binary images with continuous or linear interpolation.'. This is normal.")

    mask = tmp_mask_path
    print("temp mask created.")
        
    print("loading files. This step may take some time...")


    #import them, but catch a very specific warning and don't show it because it gets annoying
    #https://docs.python.org/3/library/warnings.html
    with warnings.catch_warnings(record=True) as w:
        subj_data = nlt.Brain_Data([subject_dir + b for b in subj_behav_design.beta],
                                  mask=mask)
        print("converting to nifti and fdata")
        t1= subj_data.to_nifti().get_fdata()

        #now we concatenate
        if spatially_concatenate:
            #need to clean first because we're combining and won't get another chance to standardize across a subject's betas
            #bd_nifti = nil.image.clean_img(subj_data.to_nifti(),detrend=False,standardize=True)
            subj_data_nifti = subj_data.to_nifti()
            sd_n_spatial_concat = spatially_concatenate_nifti_series(subj_data_nifti,zscore=False)
            if mask is not None:
                #raise Exception("masks not currently supported for spatially concatenated images")
                create_temp_mask=True
                mask_nib = nib.load(mask)
                mask_nib_bin = nil.masking.compute_brain_mask(mask_nib)
                mask_reshaped = spatially_concatenate_repeated_image(mask_nib_bin,subj_data_nifti.shape[3],zscore=False)
                nib.save(mask_reshaped,tmp_mask_path)
                print(tmp_mask_path)
                mask = tmp_mask_path
                
            subj_data = nlt.Brain_Data(sd_n_spatial_concat
                                      ,mask=mask
                                      )
            
            subj_behav_design.drop([
                'condition_index', 'condition_label',
                    'raw_beta_description', 'beta'],axis=1,inplace=True)
            subj_behav_design.drop_duplicates(inplace=True)
            
            
        print(subj_behav_design)
        subj_data.X = subj_behav_design
    na_inf_warn_count=0
    for wi in w:
        if wi.message.args[0]!='NaNs or infinite values are present in the data passed to resample. This is a bad thing as they make resampling ill-defined and much slower.':
            warnings.warn(wi.message,type(wi))
        else:
            na_inf_warn_count+=1

    if na_inf_warn_count>0:
        print("caught "+ str(na_inf_warn_count) + " instances of the warning:\n" + 
             'NaNs or infinite values are present in the data passed to resample. This is a bad thing as they make resampling ill-defined and much slower.')
        
    print('...imported data.')
    
    if create_temp_mask:
        os.remove(tmp_mask_path)
        print("temp mask deleted")
    

    return(subj_data)


def check_BD_against_test_train_set(brain_data_series,test_train_set):


    brain_data_subs=brain_data_series.X.subject.unique()

    

    holdout_subs_set = set(test_train_set[test_train_set.SplitGroup=="Holdout"].sub_label)
    train_subs_set = set(test_train_set[test_train_set.SplitGroup=="Train"].sub_label)
    holdout_data_intersection = holdout_subs_set.intersection(brain_data_subs)
    train_data_intersection = train_subs_set.intersection(brain_data_subs)

    if len(holdout_data_intersection)>0:
        del Brain_Data_allsubs
        raise Exception("The brain data contains a subject marked for holdout. Do not process!")
    else:
        print("checked for intersection and no intersection between the brain data and the subjects was found.")
        if len(train_data_intersection)==0:
            del Brain_Data_allsubs
            raise Exception("the brain data doesn't contain any of the train data. something is wrong.")
        else:
            print("there were " + str(len(train_data_intersection)) + " subjects overlapping between the subjects marked for train data and the training dump file itself.")

            
def cv_train_test_sets(
    trainset_X, trainset_y, trainset_groups,

    decoders = None,
    testset_X = None,testset_y = None, testset_groups = None,
    param_grid=None,
    cpus_to_use=-2,
    cv = None,
    regressors = None
    ):
    """
    uses a division of 'trainset' and 'testset' to allow different values to be trained and tested 
    in KFold Cross Validation. All the values are used for training and testing, but we use different ones.
    This enables us to e.g., pass in aggregated images for training and separate images for testing.

    trainset_X: x values applicalbe for TRAINING
    trainset_y
    trainset_groups: group allocations for the trainset dataset
    testset_X: values grouped into averages for testing
    testset_y
    cv: a Grouped cross-validator
    group_list: name of the groups
    """
    if regressors is not None:
        raise Exception("cv_train_test_sets 'regressors' argument is deprecated. Use 'decoders' instead. ")
    if cv is None:
        cv=KFold(n_splits=5)

    if param_grid is not None and decoders is not None:
        raise Exception('values for param_grid and decoders both passed, but param_grid is ignored if decoders is passed. choose one.')

    #if the groups we're using are actually the same.
    if (testset_X is None) and (testset_y is None):
        testset_X = trainset_X
        testset_y = trainset_y
        testset_groups = trainset_groups
        print('Groups are the same.')

    results_by_trainset_item = pd.DataFrame({
        'y': trainset_y,
        'group':trainset_groups,
        'y_pred':np.repeat(None,len(trainset_y))#,
        #'y_match':np.repeat(None,len(trainset_y))#just for debugging. delete.
    })


    groups_array = np.array(list(set(testset_groups)))
    assert(set(trainset_groups)==set(testset_groups))

    #the CV that the inner decoder uses
    cv_inner = GroupKFold(3)
    if decoders is None:
        decoders = [DecoderRegressor(standardize= False,param_grid=param_grid,cv=cv_inner,scoring="r2",
                                      n_jobs=cpus_to_use)]
        print('using default decoder, DecoderRegressor',end='. ')

    #we actually use KFold on the group names themselves, then filter across that
    #that's equivalent to doing a GroupedKFold on the data.
    test_scores = []
    results = []

    if type(cv)==type(LeaveOneOut()):
        outer_n=len(groups_array)
    else:
        outer_n = cv.get_n_splits()
    for i, x in enumerate(cv.split(groups_array)):
        train_i = x[0]
        test_i = x[1]
        print("fold " + str(i+1) + " of " + str(outer_n))

        fold_i_results = {}
        train_group_items, test_group_items = groups_array[train_i], groups_array[test_i]
        print('In order to test on a training group of ' +
              str(len(train_group_items)) + ' items, holding out the following subjects:' +
              str(test_group_items),end='. ')
#         print(
#             'held out ' + str(len(test_group_items)) + ' items and trained on ' + str(len(train_group_items)) + ' items',
#             end='. ')

        print('prepping fold data...',end='. ')
        #select training data from the averages
        #print('selecting training data',end='. ')
        train_selector = [i for i, x in enumerate(trainset_groups) if x in train_group_items]
        train_y = trainset_y[train_selector]
        train_X = nib.funcs.concat_images([trainset_X.slicer[...,s] for s in train_selector])
        train_groups = trainset_groups[train_selector]
        #print(train_X.shape,end='. ')
        #print(asizeof_fmt(train_X),end='. ')

        #select testing data from the individual values
        #print('selecting test data',end='. ')
        test_selector = [i for i, x in enumerate(testset_groups) if x in test_group_items]
        test_y = testset_y[test_selector]
        test_X = nib.funcs.concat_images([testset_X.slicer[...,s] for s in test_selector])
        test_groups = testset_groups[test_selector]
        #print(asizeof_fmt(test_X),end='. ')
        #print(test_X.shape,end='. ')


        print("fitting...",end='. ')
        print(asizeof_fmt(train_X),end='. ')

        val_scores = []
        #iterate through decoder objects.
        #this is my way of doing cross-validation across different decoders...
        hyper_scores = []
        train_results = {}
        inner_cv_results = {}
        for r_i, reg in enumerate(decoders):
            cur_r_results = {}
            print('trying decoder ' + str(r_i+1) + ' of ' + str(len(decoders)),end='. ')
            #if there is nested CV within this function the best hyper-paramters are already being chosen
            #we need only to finish the job by identifying the best overall decoder, as the final hyper-parameter
            reg.fit(y=train_y,X=train_X,groups=train_groups)
            print("predicting",end='. ')
            #hyper_score = reg.score(train_X,train_y)
            hyper_score = np.max([np.mean(param_values) for param_name, param_values in reg.cv_scores_.items()])
            #think there is a bug here. we should not have to be guessing/ignoring param names.
            #need to report this.

            hyper_scores = hyper_scores + [hyper_score]

            cur_r_results['hyper_score'] = hyper_score
            cur_r_results['cv_scores_'] = reg.cv_scores_
            cur_r_results['cv_params_'] = reg.cv_params_
            inner_cv_results[str(reg)] = cur_r_results

        fold_i_results['train_results']= inner_cv_results

        #identify which was the best
        #print(hyper_scores)
        #print(np.where([h==np.max(hyper_scores) for h in hyper_scores])[0][0])
        best_hyper_decoder = decoders[np.where([h==np.max(hyper_scores) for h in hyper_scores])[0][0]]

        #print(best_hyper_decoder)

        #now run JUST that one on this fold.


        #now predict on our test split
        test_score = best_hyper_decoder.score(test_X,test_y)
        test_y_pred = best_hyper_decoder.predict(test_X)
        fold_test_rawdata = pd.DataFrame({
            'y_obs':test_y,
            'y_pred':test_y_pred,
            'y_groups':test_groups

        })
        #results_by_trainset_item.loc[train_selector,'y_pred']
        results_by_trainset_item.loc[test_selector,'y_pred'] = test_y_pred
        #results_by_trainset_item.loc[test_selector,'y_match'] = test_y
        fold_i_results['fold_test_rawdata'] = fold_test_rawdata
        #so we can do scoring externally to this function.

        test_scores = test_scores+[test_score]
        print('test score was:',end='. ')
        print(test_score)

        results = results + [fold_i_results]

        del test_X
        del train_X
        gc.collect() #clean up. this is big data we're working with
        #https://stackoverflow.com/questions/1316767/how-can-i-explicitly-free-memory-in-python


    #We could use predefined split
#     warnings.warn(
#         "regressor was chosen based on train score across the entire train group, not the test fold of the inner CV." +
#         "Overall accuracy is not biased but this may yield a sub-optimal regressor selection." +
#         "The alternative, testing on the main holdout set, as described in the nilearn example, may overfit the data (see "+
#         "https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)." + 
#         "this problem could be addressed with the use of a PredefinedSplit." + 
#         "See https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.PredefinedSplit.html")

    return(test_scores,results,results_by_trainset_item)


def asizeof_fmt(obj, suffix='B'):
    ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
    num = asizeof(obj)
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

# for name, size in sorted(((name, asizeof(value)) for name, value in locals().items()),
#                          key= lambda x: -x[1])[:10]:


def import_wtp_w1_subjs_to_pkl(subjs,betaseries_fileid, behavioral_design,out_folder = '../data/'):
    betaseries_repo = '/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/WTP/wave1/betaseries_'
    betaseries_path = betaseries_repo + betaseries_fileid + "/"
    print(betaseries_path)
    subj_count = len(subjs)
    
    subjs.sort()
    bd_dict={}
    #get the brain data from the beta files
    for sl in subjs:
        print(sl)
        bd = get_Brain_Data_betas_for_sub(
            sl, behavioral_design,
            betaseries_path = betaseries_path
        )
        bd_dict[sl]=bd

    #now append into a concatenated brain data file
    Brain_Data_allsubs = list(bd_dict.values())[0]
    for i in range(1,len(bd_dict.values())):
        print(i)
        val_to_append = list(bd_dict.values())[i]
        Brain_Data_allsubs= Brain_Data_allsubs.append(val_to_append)

    #dump
    out_filepath = (
        '../data/Brain_Data_' +
        #'betaseries_' +
        betaseries_fileid + '_' + str(subj_count) + 'subs.pkl'
    )
    print(out_filepath)

    with open(out_filepath, 'wb') as pkl_file:
        pickle.dump(Brain_Data_allsubs,pkl_file)
        
        
def save_grouped_Brain_Data_archive_from_raw(Brain_Data_filepath):
    """
    this function takes a Brain_Data archive generated by dev_wtp_io_utils.import_wtp_w1_subjs_to_pkl
    and converts it into a Grouped Brain_Data archive, grouped by response, type, run, wave, and subject.
    The idea here is that better training may be able to be achieved with grouped data than single-trial data.
    Writes directly to file and returns the filepath of the newly created file.
    """
    print("loading pkl...")
    Brain_Data_allsubs = pickle.load(open(Brain_Data_filepath,'rb'))
    print("pkl loaded.")
    
    
    Brain_Data_allsubs_nn = Brain_Data_allsubs[Brain_Data_allsubs.X.response.isnull()==False]
    
    print("filtered by response.")
    behavioral_design = Brain_Data_allsubs_nn.X.copy()
    grouping_var_list=['response']
    run_data_list = ['type','run','wave','subject']
    #for each beta, get the key designating which group it belongs to
    behavioral_design_group_key = behavioral_design[run_data_list + grouping_var_list]
    #now just get a list of the groups from that
    grouped_subj_behavioral_design = behavioral_design_group_key.drop_duplicates().reset_index(drop=True)
    
    print("iterating through group")
    bd_list = []
    #go through each group
    group_len = grouped_subj_behavioral_design.shape[0]
    for row_i in range(group_len):
        #pull the rows of the original design that are within the group
        print(str(row_i) + " of " + str(group_len) + ", ",end='')
        beta_group = grouped_subj_behavioral_design.iloc[row_i,:]
        betas_in_group = (behavioral_design_group_key==beta_group).all(axis=1)

        #filter on that
        if(betas_in_group.sum()>1):
            group_beta = Brain_Data_allsubs_nn[betas_in_group].mean()
        else:
            group_beta = Brain_Data_allsubs_nn[betas_in_group]
        bd_list = bd_list + [group_beta]

    print('concatenating...')


        #img_list = Brain_Data_allsubs_nn[]
    bd_grouped = nlt.utils.concatenate(bd_list)
    bd_grouped.X=grouped_subj_behavioral_design
    
    
    
    filepath_out = re.sub('\.pkl$','_grouped.pkl',Brain_Data_filepath)
    print('saving ' + filepath_out)
    
    with open(filepath_out, 'wb') as pkl_file:
        pickle.dump(bd_grouped,pkl_file)

        
## get a list of the subject folders
## iterate through them
## pass in a design matrix appropriate for that subject (pretty much just subject ID and then name of condition)
## append

def import_sst_cond_w1_subjs_to_pkl(subjs,first_level_fileid,out_folder = '../data/', 
                                    conditions_to_include=None,
                                    condition_count_required=None,
                                    supplementary_df = None,
                                         out_file_suffix ='',
                                    concatenate_condition_labels=False
                                   ):
    ## get a list of the subject folders
    sst_wt_repo = '/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/SST/wave1/'
    first_level_path = sst_wt_repo + first_level_fileid + "/"
    print(first_level_path)
    subj_count = len(subjs)
    ## iterate through them
    subjs.sort()
    bd_dict={}
    #get the brain data from the beta files
    for sl in subjs:
        print(sl)
        
        #get the design data
        
        #load the matrix associated with this file
        sl_mat = scipy.io.loadmat(
            first_level_path + 'sub-' + sl +'/SPM.mat',
            simplify_cells=True            
        )

        #convert from an SPM.mat file into a dataframe list of the betas
        beta_dict_list = []
        mat_betas = sl_mat['SPM']['Vbeta']
        for beta_i in range(len(mat_betas)):
            beta = mat_betas[beta_i]
            b_description = beta['descrip']
            condition_label = re.search('Sn\(1\)\s(.*)\*bf\(1\)',b_description)
            if (condition_label is not None):
                beta_dict_list = beta_dict_list + [{
                    'condition_index':beta_i,
                    'condition_label':condition_label.group(1),
                    'raw_beta_description':beta['descrip'],
                    'beta':beta['fname']
                }]
        #    print(condition_label)
        beta_df = pd.DataFrame(beta_dict_list)

        #fill in the details related to the subject
        beta_df['subject']=sl
        beta_df['wave']=1
        
        if conditions_to_include is not None:
            #cut down conditions to just those specified
            #also ensures that the beta_df is in the ORDER SPECIFIED in conditions_to_include
            #beta_df = beta_df.loc[beta_df.condition_label.isin(conditions_to_include),]
            beta_df = pd.concat([beta_df.loc[beta_df.condition_label==cti,] for cti in conditions_to_include])

        if condition_count_required is not None:
            if beta_df.shape[0]<condition_count_required:
                print("not enough conditions for subject "+ sl + ". Skipping this subject.")
                continue
        
        
        try: 
            print(beta_df)
            bd = get_Brain_Data_betas_for_sub(
                sl, beta_df,
                betaseries_path = first_level_path,
                events_in_design=beta_df.shape[0],
                spatially_concatenate = concatenate_condition_labels,
                mask = "beta" # '/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii'
            )
            
            
            bd_dict[sl]=bd
        except BehavioralDataNotFoundForBrainDataException:
            print("couldn't get data for subject " + sl + " because there was no matching behavioral data")
    
            
    
    #now append into a concatenated brain data file
    Brain_Data_allsubs = list(bd_dict.values())[0]
    for i in range(1,len(bd_dict.values())):
        print(i)
        val_to_append = list(bd_dict.values())[i]
        Brain_Data_allsubs= Brain_Data_allsubs.append(val_to_append)
        
    if supplementary_df is not None:
        Brain_Data_allsubs.X = pd.merge(Brain_Data_allsubs.X,supplementary_df,how='left',on=['subject','wave'])

    #dump
    out_filepath = (
        out_folder + 'Brain_Data_' +
        #'betaseries_' +
        first_level_fileid + '_' + str(subj_count) + 'subs' + out_file_suffix + '.pkl'
    )
    print(out_filepath)

    with open(out_filepath, 'wb') as pkl_file:
        pickle.dump(Brain_Data_allsubs,pkl_file)

        
def import_sst_betaseries_w1_subjs_to_pkl(subjs,first_level_fileid, behavioral_design,out_folder = '../data/',
        out_file_suffix ='', mask = "beta",mask_threshold=None,
        sst_wt_repo = '/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/SST/wave1/'
                                         ):
    first_level_path = sst_wt_repo + first_level_fileid + "/"
    print(first_level_path)
    subj_count = len(subjs)
    
    subjs.sort()
    bd_dict={}
    #get the brain data from the beta files
    for sl in subjs:
        print(sl)
        
        try: 
            
            bd = get_Brain_Data_betas_for_sub(
                sl, behavioral_design,
                betaseries_path = first_level_path,
                events_in_design=behavioral_design[behavioral_design.subject==sl].shape[0],
                mask = mask, # '/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii'
                mask_threshold=mask_threshold
            )
            bd_dict[sl]=bd
        except BehavioralDataNotFoundForBrainDataException:
            print("couldn't get data for subject " + sl + " because there was no matching behavioral data")


    #now append into a concatenated brain data file
    Brain_Data_allsubs = list(bd_dict.values())[0]
    for i in range(1,len(bd_dict.values())):
        print(i)
        val_to_append = list(bd_dict.values())[i]
        Brain_Data_allsubs= Brain_Data_allsubs.append(val_to_append)

    #dump
    out_filepath = (
        out_folder + 'Brain_Data_' +
        #'betaseries_' +
        first_level_fileid + '_' + str(subj_count) + 'subs' + out_file_suffix + '.pkl'
    )
    print(out_filepath)

    with open(out_filepath, 'wb') as pkl_file:
        pickle.dump(Brain_Data_allsubs,pkl_file)
        


