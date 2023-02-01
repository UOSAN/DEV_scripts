import argparse
from collections import OrderedDict
import json
import re
import warnings
from os import PathLike
from pathlib import Path
from typing import Union, List

import numpy as np
import pandas as pd
import scipy.io

# Define some constants interpret the behavioral data
NO_RESPONSE = 0
# Key codes that correspond to random key presses
RANDOM_3_KEY = 32
RANDOM_F_KEY = 9
RANDOM_U_KEY = 24
RANDOM_UNINTERPRETABLE_KEY = 9999
#

BUTTON_BOX_2 = 90
BUTTON_BOX_3 = 91
BUTTON_BOX_4 = 92
BUTTON_BOX_5 = 93
BUTTON_BOX_6 = 94
BUTTON_BOX_7 = 95
R_KEY = 21
L_KEY = 15
LESS_THAN_KEY = 197
GREATER_THAN_KEY = 198

GO_TRIAL = 0
NO_GO_TRIAL = 1
NULL_TRIAL = 2

COUNT_NO_GO = 32
COUNT_GO = 96
COUNT_NULL = 128
COUNT_RESPONSE = 256

STUDY_ID = 'DEV'



def read_data(file: Path, use_rt_for_go_success_trials=True):
    """
    Read behavioral data out of the .mat files. The data is interpreted as follows:

    column 0 - trial number
    column 2 - trial type. 0=Go, 1=NoGo, 2=null trial (there are 96 Go, 32 NoGo, 128 null)
    column 3(?) - arrow presented
    column 6 - subject response (keycode). 0=no response.
    The participant is supposed to respond with left or right hand depending on the stimulus presented.
    Keycodes 91=left, 94=right correspond to (3, 6) buttons on button box in MRI,
    but there are some other keypress pairs that are common:
    (21, 15) correspond to ('r', 'l') keys on keyboard
    (197, 198) correspond to ('<', '>') keys on keyboard
    (92, 93) correspond to (4, 5) buttons on button box in MRI
    (90, 94) correspond to (2, 6) buttons on button box in MRI
    (94, 95) correspond to (6, 7) buttons on button box in MRI (which are on the same hand)
    column 8 - reaction time. For Go trials, this is the duration.
    column 14 - trial duration (seconds).
    column 15 - start time of trial (seconds)
    """
    mat_dict = scipy.io.loadmat(str(file), appendmat=False)
    response_data = mat_dict['Seeker']
    trial_number = response_data[:, 0]
    go_no_go_condition = response_data[:, 2]

    arrow_presented = response_data[:, 3]

    subject_response = response_data[:, 6]
    reaction_time = response_data[:, 8]

    trial_duration = response_data[:, 14]
    trial_start_time = response_data[:, 15]

    go_success = np.logical_and(go_no_go_condition == GO_TRIAL,
                                   np.logical_or(subject_response == BUTTON_BOX_3, subject_response == BUTTON_BOX_6))
    # For successful go trials, the trial only lasts until the participant reacts,
    # so replace the trial duration with the participant reaction time.
    if use_rt_for_go_success_trials:
        np.copyto(trial_duration, reaction_time, where=go_success)

    return trial_number, go_no_go_condition, subject_response, reaction_time, trial_duration, trial_start_time, arrow_presented


def read_all_data(file: Path, jitter_values: pd.Series):
    #     %%%%%%%%%%%%%% Stimuli and Response on same matsrix, pre-determined
    # % The first column is trial number;
    # % The second column is numchunks number (1-NUMCHUNKS);
    # % The third column is 0 = Go, 1 = NoGo; 2 is null, 3 is notrial (kluge, see opt_stop.m)
    # % The fourth column is 0=left, 1=right arrow; 2 is null
    # % The fifth column is ladder number (1-2);
    # % The sixth column is the value currently in "LadderX", corresponding to SSD
    # % The seventh column is subject response (no response is 0);
    # % The eighth column is ladder movement (-1 for down, +1 for up, 0 for N/A)
    # % The ninth column is their reaction time (sec)
    # reaction time is counted from the start of the arrow presentation, not the start of the trial
    # % The tenth column is their actual SSD (for error-check)
    # % The 11th column is their actual SSD plus time taken to run the command
    # % The 12th column is absolute time since beginning of task that trial begins. 
    #  That 12th column is set after the food draw event, but AFTER it is set, there is a waiting period, "OCI", before the arrow is drawn
    #   OCI is set in the "jitter" file with an extra 0.5 added. I don't think we actually record this anywhere, so 
    #   consulting that jitter file is the only way I can see to get the actual time of the arrow draw.
    # % The 13th column is the time elapsed since the beginning of the block at moment when arrows are shown
    # % The 14th column is the actual SSD for error check (time from arrow displayed to beep played)
    # % The 15th column is the duration of the trial from trialcode
    # the trial will end as the subject presses a button
    # % The 16th column is the time_course from trialcode
    # % The 17th column is the UvH code (0=unhealthy, 1=healthy, 2=null)

    mat_dict = scipy.io.loadmat(str(file), appendmat=False)
    response_data = pd.DataFrame(mat_dict['Seeker'])
    #give names to the columns
    response_data.columns = [
        'trial_number', 'numchunks', 'go_no_go_condition', 'arrow_presented', 'ladder_number', 
        'ssd', 'subject_response', 'ladder_movement', 'reaction_time', 
        'actual_ssd', 'actual_ssd_plus_time', 'absolute_time', 'time_elapsed', 
        'actual_ssd_error_check', 'trial_duration', 'time_course', 'uvh_code']

    #these are additional pieces of information to clarify how this data is processed.
    #combine in the jitter_values
    jitter_values_df = pd.DataFrame({'trial_number':[t*2+1 for t in range(len(jitter_values))], 'jitter_value':jitter_values})
    response_data = response_data.merge(jitter_values_df, on='trial_number', how='left')  
    response_data['OCI'] = 0.5 + response_data.jitter_value
    response_data['arrow_start_time_calculated'] = response_data['OCI'] + response_data['absolute_time']
    response_data['reaction_onset'] = response_data['arrow_start_time_calculated'] + response_data['reaction_time']
    has_tone = response_data['actual_ssd_error_check'] > 0
    response_data.loc[has_tone,'tone_onset'] = response_data.loc[has_tone,'arrow_start_time_calculated'] + response_data.loc[has_tone,'actual_ssd_error_check']
    response_data['trial_end']=response_data['time_course']+response_data['trial_duration']

    return (response_data)

    


def create_masks(condition: np.ndarray, response: np.ndarray) -> List:
    """Create masks of conditions"""
    temp = np.logical_or.reduce((response == NO_RESPONSE, response == RANDOM_3_KEY,
                                    response == RANDOM_F_KEY, response == RANDOM_U_KEY,
                                    response == RANDOM_UNINTERPRETABLE_KEY))
    go_fail = np.logical_and(condition == GO_TRIAL, temp)
    temp = np.logical_or.reduce((response == BUTTON_BOX_3, response == BUTTON_BOX_6,
                                    response == BUTTON_BOX_4, response == BUTTON_BOX_5,
                                    response == R_KEY, response == L_KEY,
                                    response == LESS_THAN_KEY, response == GREATER_THAN_KEY,
                                    response == BUTTON_BOX_2, response == BUTTON_BOX_7))
    go_success = np.logical_and(condition == GO_TRIAL, temp)

    no_go_fail = np.logical_and(condition == NO_GO_TRIAL, response != NO_RESPONSE)
    no_go_success = np.logical_and(condition == NO_GO_TRIAL, response == NO_RESPONSE)

    null_trials = (condition == NULL_TRIAL)

    return list((go_success, no_go_success, no_go_fail, null_trials, go_fail))

def get_pss(condition_masks: List,posterror_masks_dict: List,reaction_time:np.ndarray):
    go_success = condition_masks[0]
    no_go_success = condition_masks[1]
    no_go_fail = condition_masks[2]

    #for each of those, check if we have both a pre-trial correct go an a post-trial correct go
    #if we do, compute the difference and return that
    #otherwise the result is null
    def get_pss_for_stop_trials(stop_trials):
        #we need the position of each stop trial, then look ahead and behind
        #next
        #pss = np.empty(len(stop_trials),dtype=float)
        pss = []
        for i in range(0,len(stop_trials)):
            is_stop_trial = stop_trials[i]
            #if it's stop trial we gotta return either None or a value
            if is_stop_trial:
                #if we have the post-stop go trial and it's a correct go
                # get the reaction times before and after
                # get reaction times actually two steps before
                # and if they're both valid items, take the mean
                # get the difference
                if (i+2)<len(stop_trials) and go_success[i+2]:
                    if (i-4)>0 and go_success[i-4] and go_success[i-2]:
                        baseline = np.mean([reaction_time[i - 4], reaction_time[i - 2]])
                    elif (i-2)>0 and go_success[i-2]:
                        baseline = reaction_time[i - 2]
                    elif (i-4)>0 and go_success[i-4]:
                        baseline = reaction_time[i - 4]
                    else:
                        baseline = np.nan
                    pss_i = reaction_time[i + 2] - baseline
                else:
                    pss_i = np.nan
                pss = pss + [pss_i]

        return(pss)

    no_go_success_pss = get_pss_for_stop_trials(no_go_success)
    no_go_fail_pss = get_pss_for_stop_trials(no_go_fail)

    pss_by_trial = np.array([np.nan]*len(reaction_time))
    pss_by_trial[no_go_success] = no_go_success_pss
    pss_by_trial[no_go_fail] = no_go_fail_pss
    
    return({
        'by_poststop_trial_type':{
            'CorrectGoFollowingCorrectStop': pss_by_trial[list(posterror_masks_dict['CorrectGoFollowingCorrectStop'][2:]) + [False, False]],
            'CorrectGoFollowingFailedStop': pss_by_trial[list(posterror_masks_dict['CorrectGoFollowingFailedStop'][2:]) + [False, False]],
        },
        'by_stop_trialtype':{
            'no_go_success_pss':no_go_success_pss,
            'no_go_fail_pss':no_go_fail_pss},
        'by_trial': pss_by_trial
        }
        )


def create_posterror_masks_from_masks(condition_masks: List) -> List:
    """Create masks of post-error slowing conditions, derived from the original set of masks"""

    go_success = condition_masks[0]
    no_go_success = condition_masks[1]
    no_go_fail = condition_masks[2]
    null_trials = condition_masks[3]
    go_fail = condition_masks[4]

    # marks if each trial is a (successful or failed) go that follows a failed stop
    # we shift by 2, not 1, because we ignore the "NULL TRIAL" that occurs reliably every second trial
    go_success_following_failed_stop = np.append([False, False],
                                                    (go_success[2:] & no_go_fail[:(len(no_go_fail) - 2)]))
    failed_stop_preceding_go_success = np.append(   (go_success[2:] & no_go_fail[:(len(no_go_fail) - 2)]),
                                                [False, False])

    # marks if each trial is a (successful or failed) go that follows a successful stop
    go_success_following_successful_stop = np.append([False, False],
                                                        (go_success[2:] & no_go_success[:(len(no_go_success) - 2)]))
    successful_stop_preceding_go_success = np.append(   (go_success[2:] & no_go_success[:(len(no_go_success) - 2)]),
                                                [False, False])

    no_go_fail_other = no_go_fail & (failed_stop_preceding_go_success==False)
    no_go_success_other = no_go_success & (successful_stop_preceding_go_success==False)
    

    # create one beta for all the other SuccessGo trials
    other_successful_go = go_success & (go_success_following_successful_stop == False) & (
            go_success_following_failed_stop == False)
    # then just pass on the other masks as returned from create_masks

    # other_failed_go = go_fail & (go_following_successful_stop==False) & (go_following_failed_stop==False)

    # ['GoFollowingCorrectStop', 'GoFollowingFailedStop',
    # 'OtherCorrectGo', 'CorrectStop', 'FailedStop', 'Cue', 'OtherFailedGo'
    #Why you should use an OrderedDict even though dicts are ordered in python 3.6+
    #TLDR: can't guarantee someone will run this in 3.6+ and it's not worth the risk
    #https://gandenberger.org/2018/03/10/ordered-dicts-vs-ordereddict/
    return (OrderedDict({
        'CorrectGoFollowingCorrectStop': go_success_following_successful_stop,
        'CorrectGoFollowingFailedStop': go_success_following_failed_stop,
        'OtherCorrectGo': other_successful_go, 
        'CorrectStopPrecedingCorrectGo': successful_stop_preceding_go_success,
        'FailedStopPrecedingCorrectGo': failed_stop_preceding_go_success,
        'OtherCorrectStop': no_go_success_other,
        'OtherFailedStop': no_go_fail_other,
        'Cue': null_trials, 
        'OtherFailedGo': go_fail
    }))

def create_posterror_cue_masks_from_masks(condition_masks: List) -> List:
    """
    Create masks of post-error slowing conditions, derived from the original set of masks
    Also includes classifying cue trials into post-error and non-post-error
    """

    go_success = condition_masks[0]
    no_go_success = condition_masks[1]
    no_go_fail = condition_masks[2]
    null_trials = condition_masks[3]
    go_fail = condition_masks[4]

    # marks if each trial is a (successful or failed) go that follows a failed stop
    # we shift by 2, not 1, because we ignore the "NULL TRIAL" that occurs reliably every second trial
    go_success_following_failed_stop = np.append([False, False],
                                                    (go_success[2:] & no_go_fail[:(len(no_go_fail) - 2)]))
    failed_stop_preceding_go_success = np.append(   (go_success[2:] & no_go_fail[:(len(no_go_fail) - 2)]),
                                                [False, False])

    # marks if each trial is a (successful or failed) go that follows a successful stop
    go_success_following_successful_stop = np.append([False, False],
                                                        (go_success[2:] & no_go_success[:(len(no_go_success) - 2)]))
    successful_stop_preceding_go_success = np.append(   (go_success[2:] & no_go_success[:(len(no_go_success) - 2)]),
                                                [False, False])

    no_go_fail_other = no_go_fail & (failed_stop_preceding_go_success==False)
    no_go_success_other = no_go_success & (successful_stop_preceding_go_success==False)

    #mark cues into following failed stop, following successful stop, and other
    cue_following_failed_stop = np.append(
        [False],(null_trials[1:] & no_go_fail[:(len(no_go_fail) - 1)])) 
    cue_following_successful_stop = np.append(
        [False],(null_trials[1:] & no_go_success[:(len(no_go_success) - 1)]))
    cue_other = null_trials & (cue_following_failed_stop==False) & (cue_following_successful_stop==False)   
    

    # create one beta for all the other SuccessGo trials
    other_successful_go = go_success & (go_success_following_successful_stop == False) & (
            go_success_following_failed_stop == False)
    # then just pass on the other masks as returned from create_masks

    # other_failed_go = go_fail & (go_following_successful_stop==False) & (go_following_failed_stop==False)

    # ['GoFollowingCorrectStop', 'GoFollowingFailedStop',
    # 'OtherCorrectGo', 'CorrectStop', 'FailedStop', 'Cue', 'OtherFailedGo'
    #raise Exception("TO DO: RUN THE POSTERROR SCRIPT TO USE THIS NEW ORDER, THEN FOLLOW THE PROCESS TO UPLOAD TO TALAPAS, DO LEVEL 1, THEN DOWNLOAD AND DO LEVEL 2")
    #raise Exception("TO DO: AT THIS POINT JUST ADD A CONTRAST FOR THE NO RT ANALYSIS. DON'T THINK WE NEED ONE FOR THE RT ANALYSIS")
    return ({
        'CueFollowingCorrectStop': cue_following_successful_stop,
        'CueFollowingFailedStop': cue_following_failed_stop,
        'CorrectGoFollowingCorrectStop': go_success_following_successful_stop,
        'CorrectGoFollowingFailedStop': go_success_following_failed_stop,
        'CorrectStopPrecedingCorrectGo': successful_stop_preceding_go_success,
        'FailedStopPrecedingCorrectGo': failed_stop_preceding_go_success,
        'OtherCue': cue_other,
        'OtherCorrectGo': other_successful_go, 
        'OtherCorrectStop': no_go_success_other,
        'OtherFailedStop': no_go_fail_other,
        'OtherFailedGo': go_fail
    })

def create_event_conditions(main_dataset: pd.DataFrame, jitter_values: List) -> OrderedDict:
    
    """Create an event-related set of conditions"""
    # temp = np.logical_or.reduce((response == NO_RESPONSE, response == RANDOM_3_KEY,
    #                                 response == RANDOM_F_KEY, response == RANDOM_U_KEY,
    #                                 response == RANDOM_UNINTERPRETABLE_KEY))
    # go_fail = np.logical_and(condition == GO_TRIAL, temp)
    # go_success = np.logical_and(condition == GO_TRIAL, temp)

    # no_go_fail = np.logical_and(condition == NO_GO_TRIAL, response != NO_RESPONSE)
    # no_go_success = np.logical_and(condition == NO_GO_TRIAL, response == NO_RESPONSE)

    # null_trials = (condition == NULL_TRIAL)
    #set up some extra variables we'll need

    #     %%%%%%%%%%%%%% Stimuli and Response on same matsrix, pre-determined
    # % The first column is trial number;
    # % The second column is numchunks number (1-NUMCHUNKS);
    # % The third column is 0 = Go, 1 = NoGo; 2 is null, 3 is notrial (kluge, see opt_stop.m)
    # % The fourth column is 0=left, 1=right arrow; 2 is null
    # % The fifth column is ladder number (1-2);
    # % The sixth column is the value currently in "LadderX", corresponding to SSD
    # % The seventh column is subject response (no response is 0);
    # % The eighth column is ladder movement (-1 for down, +1 for up, 0 for N/A)
    # % The ninth column is their reaction time (sec)
    # % The tenth column is their actual SSD (for error-check)
    # % The 11th column is their actual SSD plus time taken to run the command
    # % The 12th column is absolute time since beginning of task that trial begins
    # % The 13th column is the time elapsed since the beginning of the block at moment when arrows are shown
    # % The 14th column is the actual SSD for error check (time from arrow displayed to beep played)
    # % The 15th column is the duration of the trial from trialcode
    # % The 16th column is the time_course from trialcode
    # % The 17th column is the UvH code (0=unhealthy, 1=healthy, 2=null)
    main_dataset['preceding_go_no_go_condition'] = main_dataset.go_no_go_condition.shift(2, fill_value=0)
    #main_dataset['preceding_go_no_go_condition'] = main_dataset.go_no_go_condition.shift(2, fill_value=0)

    

    response = main_dataset.subject_response
    main_dataset['go_response'] = np.logical_or.reduce((response == BUTTON_BOX_3, response == BUTTON_BOX_6,
                                    response == BUTTON_BOX_4, response == BUTTON_BOX_5,
                                    response == R_KEY, response == L_KEY,
                                    response == LESS_THAN_KEY, response == GREATER_THAN_KEY,
                                    response == BUTTON_BOX_2, response == BUTTON_BOX_7))

    main_dataset['preceding_go_response'] = main_dataset.go_response.shift(2, fill_value=False)


    #for each trial type, create one list of onsets and one list of durations

    #1. trial
    #we have SEVEN different trial conditions
    #CS, FS, CGFFS, CGFCS, CGFCG, CGFFG, CGO
    trial_following_go_onset = main_dataset.loc[main_dataset.preceding_go_no_go_condition==GO_TRIAL]['time_course']
    trial_following_correct_stop_onset = main_dataset.loc[(main_dataset.preceding_go_no_go_condition==NO_GO_TRIAL) & (main_dataset.preceding_go_response==False)]['time_course']
    trial_following_failed_stop_onset = main_dataset.loc[(main_dataset.preceding_go_no_go_condition==NO_GO_TRIAL) & (main_dataset.preceding_go_response)]['time_course']
    trial_other_onset = main_dataset.loc[main_dataset.preceding_go_no_go_condition==NULL_TRIAL]['time_course']
    trial_following_go_duration = main_dataset.loc[main_dataset.preceding_go_no_go_condition==GO_TRIAL]['trial_duration']
    trial_following_correct_stop_onset = main_dataset.loc[(main_dataset.preceding_go_no_go_condition==NO_GO_TRIAL) & (main_dataset.preceding_go_response==False)]['trial_duration']
    trial_following_failed_stop_onset = main_dataset.loc[(main_dataset.preceding_go_no_go_condition==NO_GO_TRIAL) & (main_dataset.preceding_go_response)]['trial_duration']
    trial_other_duration = main_dataset.loc[main_dataset.preceding_go_no_go_condition==NULL_TRIAL]['trial_duration']

    #2. Response
    # I want to ignore which key they are pressing for now...
    #we have 2 different response conditions, ignoring which key they are pressing
    # We'll just classify them as correct or incorrect
    response_correct_onset = main_dataset.loc[main_dataset.go_response==True]['time_course'] + main_dataset.loc[main_dataset.go_response==True]['reaction_time']
    response_incorrect_onset = main_dataset.loc[main_dataset.go_response==True]['time_course'] + main_dataset.loc[main_dataset.go_response==True]['reaction_time']


    # marks if each trial is a (successful or failed) go that follows a failed stop

    #will need to edit these to not use masks
    names = []
    onsets = []
    durations = []
    for i, cond_name in enumerate(condition_labels):
        mask = masks[i]
        if sum(mask) > 0:
            names = names + [cond_name]
            cond_onset = start_time[mask].reshape(np.count_nonzero(mask), 1)
            onsets = onsets + [cond_onset]
            cond_duration = duration[mask].reshape(np.count_nonzero(mask), 1)
            durations = durations + [cond_duration]

    #names is a list of each of the conditions
    #onsets is a list of the onsets of each kind 
    conditions = {'names': np.asarray(names, dtype=np.object),
                  'onsets': onsets,
                  'durations': durations}




def create_trials(trial_number: np.ndarray, trial_start_time: np.ndarray, trial_duration: np.ndarray,
                  subject_response: np.ndarray):
    # Output names (trial number or condition name (GoFail, GoSuccess, NoGoFail, NoGoSuccess)),
    # onsets (when the thing started),
    # durations (how long the thing lasted)
    names = np.asarray(trial_number, dtype=np.object)
    onsets = np.asarray(trial_start_time, dtype=np.object)
    durations = np.asarray(trial_duration, dtype=np.object)
    raw_response = np.asarray(subject_response, dtype=np.object)

    trials = {'names': names,
              'onsets': onsets,
              'durations': durations}
    return trials


def create_conditions(start_time: np.ndarray, duration: np.ndarray, masks: List,
                      condition_labels: List = ['CorrectGo', 'CorrectStop', 'FailedStop', 'Cue', 'FailedGo']):
    # redesign 2021-10 BJS which only adds conditions with a non-zero amount of trials.
    names = []
    onsets = []
    durations = []
    for i, cond_name in enumerate(condition_labels):
        mask = masks[i]
        if sum(mask) > 0:
            names = names + [cond_name]
            cond_onset = start_time[mask].reshape(np.count_nonzero(mask), 1)
            onsets = onsets + [cond_onset]
            cond_duration = duration[mask].reshape(np.count_nonzero(mask), 1)
            durations = durations + [cond_duration]

        else:
            warnings.warn(
                "condition " + cond_name + " has no actual trials for current subject. Depending on the condition, some analyses may assume the condition exists so this may present a problem.")
            # raise Exception()
    #     names = np.asarray(['CorrectGo', 'CorrectStop', 'FailedStop', 'Cue', 'FailedGo'], dtype=np.object)
    #     onsets = np.zeros((len(masks),), dtype=np.object)
    #     durations = np.zeros((len(masks),), dtype=np.object)
    # onsets and durations have to be reshaped from 1-d np arrays to Nx1 arrays so when written
    # by scipy.io.savemat, the correct cell array is created in matlab
    # if a mask has no true values then it's effectively empty.
    #     for i, mask in enumerate(masks):
    #         onsets[i] = start_time[mask].reshape(np.count_nonzero(mask), 1)
    #         durations[i] = duration[mask].reshape(np.count_nonzero(mask), 1)

    conditions = {'names': np.asarray(names, dtype=np.object),
                  'onsets': onsets,
                  'durations': durations}
    return conditions


def create_posterror_conditions(start_time: np.ndarray, duration: np.ndarray, posterror_masks: List):
    condition_labels = ['CorrectGoFollowingCorrectStop', 'CorrectGoFollowingFailedStop',
                        'OtherCorrectGo', 'CorrectStopPrecedingCorrectGo', 'FailedStopPrecedingCorrectGo', 'CorrectStopOther', 'FailedStopOther', 'Cue', 'FailedGo']
    return (create_conditions(start_time, duration, posterror_masks, condition_labels=condition_labels))


def write_betaseries(output_dir: Union[PathLike, str], subject_id: str, wave: str, trials):
    path = Path(output_dir) / 'betaseries'
    # path = Path('betaseries')
    path.mkdir(parents=True, exist_ok=True)
    file_name = f'DEV{subject_id}_{wave}_SST1.mat'

    scipy.io.savemat(str(path / file_name), trials)


def write_beta_data(output_dir: Union[PathLike, str], subfolder, subject_id: str, wave: str, trials):
    path = Path(output_dir) / subfolder
    # path = Path(subfolder)
    path.mkdir(parents=True, exist_ok=True)
    file_name = f'DEV{subject_id}_{wave}_SST1.mat'

    scipy.io.savemat(str(path / file_name), trials)
    
    print('created file at ' + str(path / file_name))


def write_bids_events(input_dir: Union[PathLike, str], subject_id: str, wave: str, trials):
    # Write the events.tsv to BIDS only if the BIDS structure already exists
    subject_path = Path(input_dir) / f'sub-{STUDY_ID}{subject_id}'
    if subject_path.exists():
        path = Path(input_dir) / f'sub-{STUDY_ID}{subject_id}' / f'ses-wave{wave}'
        if wave == '1' or wave == '2':
            path = path / 'func'
        else:
            path = path / 'beh'

        path.mkdir(parents=True, exist_ok=True)
        file_name = Path(f'sub-{STUDY_ID}{subject_id}_ses-wave{wave}_task-SST_acq-1_events.tsv')

        np.savetxt(str(path / file_name),
                      trials,
                      delimiter='\t',
                      header='onset\tduration\ttrial_type\tpresented\tresponse',
                      comments='',
                      fmt=['%10.5f', '%10.5f', '%s', '%10.5f', '%s'])

        file_name = Path(f'sub-{STUDY_ID}{subject_id}_ses-wave{wave}_task-SST_acq-1_events.json')
        write_events_description(path, file_name)


def write_events_description(path: Path,
                             file_name: Path):
    desc = {
        "onset": {
            "LongName": "Onset",
            "Description": "Onset of the event measured from the beginning of the acquisition of "
                           "the first volume in the corresponding task imaging data file.",
            "Units": "s"
        },
        "duration": {
            "LongName": "Duration",
            "Description": "Duration of the event, measured from onset.",
            "Units": "s"
        },
        "trial_type": {
            "LongName": "Categorization of a response inhibition task",
            "Description": "Education level, self-rated by participant",
            "Levels": {
                "correct-go": "Go trial, correct response",
                "failed-go": "Go trial, incorrect or no response",
                "correct-stop": "No-go or stop trial, correct response",
                "failed-stop": "No-go or stop trial, incorrect response",
                "null": "Null trial where cue stimulus is presented for duration"
            }
        },
        "presented": {
            "LongName": "presented arrow to the subject",
            "Description": "arrow presetned to the subject; 0=left, 1=right, 2=null"
        },
        "response": {
            "LongName": "preprocessed categorization of the subject response.",
            "Description": "subject response"
        }
    }
    with open(str(path / file_name), 'w') as f:
        json.dump(desc, f, indent=4)


# for debugging, can help to summarize what's inside the mask.
def print_mask_signature(masks):
    if type(masks) is dict or type(masks) is OrderedDict:
        print([k + ':'+ str(np.sum(masks[k])) + ' True of ' + (str(len(masks[k]))) for k in masks])
    else:
        print([str(np.sum(m)) + ' True of ' + (str(len(m))) for m in masks])
    # print(np.sum([np.sum(m) for m in masks]))


# takes a raw ascii response and returns a left or right keypress if the keypress can be categorized as either of those
# otherwise it returns an 'invalid response' signal, distinct from other responses
def clean_response_data(raw_response: np.ndarray, arrow_presented: np.ndarray):
    # The participant is supposed to respond with left or right hand depending on the stimulus presented.
    # Keycodes 91=left, 94=right correspond to (3, 6) buttons on button box in MRI,
    # but there are some other keypress pairs that are common:
    # (21, 15) correspond to ('r', 'l') keys on keyboard
    # (197, 198) correspond to ('<', '>') keys on keyboard
    # (92, 93) correspond to (4, 5) buttons on button box in MRI
    # (90, 94) correspond to (2, 6) buttons on button box in MRI
    # (94, 95) correspond to (6, 7) buttons on button box in MRI (which are on the same hand)
    # this is really best done considering a list of responses.

    # we get a tally, we consider that the most common two items are left and right,
    # and then see if they fit any of the pairs we recognize. if we don't the whole dataset might be off.
    item_responses = np.unique(raw_response[raw_response != 0], return_counts=True)

    item_order = (-item_responses[1]).argsort()
    most_common_two_responses = np.take(item_responses[0], item_order)[0:2]

    labelled_responses = [None] * len(raw_response)
    # BUTTON_BOX_2 = 90
    # BUTTON_BOX_3 = 91
    # BUTTON_BOX_4 = 92
    # BUTTON_BOX_5 = 93
    # BUTTON_BOX_6 = 94
    # BUTTON_BOX_7 = 95
    # R_KEY = 21
    # L_KEY = 15
    # LESS_THAN_KEY = 197
    # GREATER_THAN_KEY = 198

    # try to identify the code the subject has used.
    # if set(most_common_two_responses)==set([BUTTON_BOX_3,BUTTON_BOX_6]):
    #     # left_code = BUTTON_BOX_3
    #     # right_code = BUTTON_BOX_6
    #     print(item_responses)
    # elif set(most_common_two_responses)==set([BUTTON_BOX_3,BUTTON_BOX_6]):
    # else:
    #     print("couldn't identify button pair")
    # print(item_responses)
    # print("most common responses: ")
    # print(most_common_two_responses)

    counts = pd.DataFrame({
        'presented': arrow_presented,
        'pressed': raw_response
    }
    ).groupby(['presented', 'pressed']).aggregate(len)

    left_responses = [91, 197, 15, 92]  # also include:90? 94
    right_responses = [94, 198, 21, 93]  # also include: 95 (vs. 94)
    for i in range(len(raw_response)):
        # special case where most common items were 94 and 95, 94 should be mapped to left and 95 should be mapped to right
        if set(most_common_two_responses) == set([94, 95]):
            if raw_response[i] == 94:
                labelled_responses[i] = 'left'
            elif raw_response[i] == 95:
                labelled_responses[i] = 'right'
            next
        # otherwise we carry on to the normal labelling
        if raw_response[i] in left_responses:
            labelled_responses[i] = 'left'
        elif raw_response[i] in right_responses:
            labelled_responses[i] = 'right'
        elif raw_response[i] == 0:
            pass
        else:
            print("raw response unidentified")
            print(raw_response[i])
            labelled_responses[i] = 'invalid'

    return (labelled_responses)


def save_varying_condition_list(output_folder: str, subfolder: str, file_condition_dict: dict,
                                target_conditions: List):
    # for the purposes of the post-error analysis, we need to put these into two groups:
    # runs that contain both 'CorrectGoFollowingCorrectStop' and 'CorrectGoFollowingFailedStop'; and runs that do not contain either.
    # that should be straightforward enough...we might also want to do this separately for each wave.

    complete_list_by_wave = {}
    for sub, wave in file_condition_dict:
        s_w_cond_list = file_condition_dict[(sub, wave)]
        #print(s_w_cond_list)
        target_condition_count = len(set(target_conditions))
        target_conditions_present_count = len(
            set(target_conditions).intersection(set(s_w_cond_list))
        )
        if wave not in complete_list_by_wave.keys():
            complete_list_by_wave[wave] = {}
            complete_list_by_wave[wave]['complete'] = []
            complete_list_by_wave[wave]['missing'] = []

        if target_conditions_present_count == target_condition_count:
            complete_list_by_wave[wave]['complete'].append(sub)
        elif target_conditions_present_count < target_condition_count:
            complete_list_by_wave[wave]['missing'].append(sub)
        else:
            raise Exception("more conditions present in data than in target conditions")

    # now save the lists
    for wave in complete_list_by_wave.keys():
        for condition_class in complete_list_by_wave[wave]:
            condition_complete_folder = Path(output_folder) / subfolder
            condition_complete_folder.mkdir(parents=True, exist_ok=True)
            condition_complete_filepath = str(condition_complete_folder / (condition_class + "_" + str(wave) + ".txt"))
            subject_count = len(complete_list_by_wave[wave][condition_class])
            print("writing " + condition_complete_filepath + " with " + str(subject_count) + " subjects.")
            # path = Path(subfolder)

            with open(condition_complete_filepath, 'w') as filehandle:
                for listitem in complete_list_by_wave[wave][condition_class]:
                    filehandle.write('DEV%s\n' % listitem)


def main(input_dir: str, bids_dir: str = None, file_limit=None,
         use_rt_for_go_success_trials=True,
         output_folder=""):
    print(input_dir)

    files = list(Path(input_dir).glob('DEV*.mat'))
    files.sort()
    pattern = 'DEV(\\d{3})_run(\\d{1})_.*.mat'
    # pattern = 'DEV(\\d{3})_(\\d{1})_SST1\\.mat'

    # for testing
    if file_limit is not None:
        files = files[0:file_limit]

    file_condition_index = {}
    file_condition_index['conditions'] = {}
    multicond_df_list = []


    for f in files:
        match = re.search(pattern, str(f.name))
        if match:
            subject_id, wave_number = match.groups()
            print(f.name)

            # Read data out of the .mat file
            trial_number, go_no_go_condition, subject_response, reaction_time, trial_duration, trial_start_time, arrow_presented = \
                read_data(f, use_rt_for_go_success_trials=use_rt_for_go_success_trials)

            # Create masks for the various conditions
            masks = create_masks(go_no_go_condition, subject_response)
            print_mask_signature(masks)

            # create masks for the post-error slowing
            # posterror_masks = create_posterror_masks_from_masks(masks)
            # print_mask_signature(posterror_masks)

            # Perform some quality checking on the numbers of responses (should be 256),
            # the number of null trials (should be 128),
            # go trials (should be 96), and no-go trials (should be 32)
            if subject_response.size != COUNT_RESPONSE:
                print(f'Wrong number of responses   : (subject, expected, actual) '
                      f'({subject_id}, {COUNT_RESPONSE}, {subject_response.size})')
            if np.count_nonzero(masks[0] + masks[-1]) != COUNT_GO:
                print(f'Wrong number of go trials : (subject, run, expected, actual) '
                      f'({subject_id}, {wave_number}, {COUNT_GO}, {np.count_nonzero(masks[0] + masks[-1])})')
            if np.count_nonzero(masks[1] + masks[2]) != COUNT_NO_GO:
                print(f'Wrong number of no-go trials: (subject, expected, actual) '
                      f'({subject_id}, {COUNT_NO_GO}, {np.count_nonzero(masks[1] + masks[2])})')
            if np.count_nonzero(masks[3]) != COUNT_NULL:
                print(f'Wrong number of null trials : (subject, expected, actual) '
                      f'({subject_id}, {COUNT_NULL}, {np.count_nonzero(masks[3])})')

            # preprocess subject responses for attention check
            cleaned_subject_response = clean_response_data(subject_response, arrow_presented)

            if bids_dir:  # create MAT files storing behavioral information in bids format
                print("creating bids events")
                trial_type = np.empty_like(trial_number, dtype=np.object)
                trial_type_names = ['correct-go', 'correct-stop', 'failed-stop', 'null', 'failed-go']
                for mask, name in zip(masks, trial_type_names):
                    np.putmask(trial_type, mask, name)
                write_bids_events(bids_dir, subject_id, wave_number,
                                  np.stack(
                                      (trial_start_time, trial_duration, trial_type, arrow_presented,
                                       cleaned_subject_response), axis=1))
            else:
                print("creating betaseries and conditions")
                # create onset files for SPM first-level analysis
                trials = create_trials(trial_number, trial_start_time, trial_duration, subject_response)

                trial_df_row = pd.DataFrame({
                    'subject_id':subject_id,
                    'wave_number':wave_number,
                    'trial_number': trial_number, 
                    'go_no_go_condition': go_no_go_condition, 
                    'subject_response': subject_response, 
                    'reaction_time': reaction_time,
                    'trial_duration': trial_duration, 
                    'trial_start_time': trial_start_time, 
                    'arrow_presented': arrow_presented})

                multicond_df_list = multicond_df_list + [trial_df_row]
                # Create paths and file names
                write_betaseries(output_folder, subject_id, wave_number, trials)

                conditions = create_conditions(trial_start_time, trial_duration, masks)
                write_beta_data(output_folder, 'conditions', subject_id, wave_number, conditions)

                # file_condition_index['conditions'][(subject_id, wave_number)] = conditions['names']



                # posterror_conditions = create_posterror_conditions(trial_start_time, trial_duration, posterror_masks)
                # write_beta_data(output_folder, 'posterror_conditions', subject_id, wave_number, posterror_conditions)
                print("written data for subject " + str(subject_id))
        else:
            print("match not found for " + str(f.name))

    multicond_df = pd.concat(multicond_df_list)
    multicond_df.to_csv(output_folder + "_multicond_out.csv")
    

    #removed because there are multiple sets of target conditions, and in the end I decided to deal with the variance in contrasts a different way.
    # save_varying_condition_list(output_folder=output_folder,
    #                             subfolder="conditions",
    #                             file_condition_dict=file_condition_index['conditions'],
    #                             target_conditions=['Cconditions=['CorrectGo',
    #                                                'CorrectStop'])



if __name__ == "__main__":
    description = 'Create multi-condition files for SST task in DEV study'
    print(description)

    parser = argparse.ArgumentParser(description=description,
                                     add_help=True,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--input', metavar='Input directory', action='store',
                        type=str, required=True,
                        help='absolute path to directory containing behavioral output from the SST task.',
                        dest='input_dir'
                        )
    parser.add_argument('-b', '--bids', metavar='BIDS directory', action='store',
                        type=str, required=False, default=None,
                        help='absolute path to your top level bids folder.',
                        dest='bids_dir'
                        )

    args = parser.parse_args()

    raise Exception("Deprecated this version of multiconds. use multiconds full duration instead.")

    main(args.input_dir, args.bids_dir)
