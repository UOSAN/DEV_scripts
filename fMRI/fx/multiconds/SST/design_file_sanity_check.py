#open the level-1 design files and look to see if they broadly match what we expect based (a) raw data in the drop box and (b) the behavioral compilation file I have created


#load the behavioral compilation file
import numpy as np
from pathlib import Path
import re
import pandas as pd
from utils import read_yaml_for_host

import scipy.io


#input_dir = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/posterror_cues'
input_dir = '/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/posterror_conditions_w_pss'


config_data = read_yaml_for_host("sst_l1_paths.yml")
supplemental_data_path = config_data['supplemental_data_path']
sst_raw_data_path = config_data['sst_raw_data_path']

preprocessed_behavioral_data = pd.read_csv(supplemental_data_path)



files = list(Path(input_dir).glob('DEV*.mat'))
    
files.sort()

pattern = "DEV(\\d{3})_(\\d*).*.mat"

raw_file_pattern = "DEVID_runRUNID_.*.mat"

#create an empty dataframe to columns for subject ID, wave ID, condition name, and number of trials
trial_count_df = pd.DataFrame(columns=['subject_id','wave_id','condition_name','trial_count'])

#randomize the file list so we can pick a randomly selected subject
np.random.shuffle(files)

#get the raw files. we'll just load the full list now and draw from it later
raw_files = list(Path(sst_raw_data_path).glob('DEV*.mat'))


#print out the subject ID and wave ID in each filename based on the pattern
for f in files:
    match = re.search(pattern, str(f.name))

    

    if match:
        subject_id, wave_number = match.groups()
        print(f.name +  "; subject " + subject_id + "; wave " + wave_number)

        #now open up the .mat file for reading
        mat_dict = scipy.io.loadmat(str(f), appendmat=False)

        condition_names = mat_dict['names'][0]

        #get the preprocessed behavioral data for this condition
        subj_wave_behavioral_data = preprocessed_behavioral_data.loc[
            (preprocessed_behavioral_data['subid']==('DEV' + subject_id)) & (preprocessed_behavioral_data['waveid']==int(wave_number))]
        #sort it by trial number
        subj_wave_behavioral_data = subj_wave_behavioral_data.sort_values(by=['trial_n'])

        #for each condition in condition_names,
        #grab the trials matching those conditions from the behavioral data, along with their onsets and durations.
        #regex match on each row of the condition column
        
        print("condition names we have for this subject:")
        print(condition_names)

        for condition_i, condition_name in enumerate(condition_names):
            #match strategy 1--find the condition name in the beahvioral data column
            print(condition_name)
            
            # condition_match_1 = [bool(re.match(condition_name[0], bdc)) for bdc in subj_wave_behavioral_data.condition]
            # #this won't work because the condition names are quite long--therefore we need to do the match in reverse--see if the trial label is in the condition name
            # condition_match_2 = [bool(re.match(bdc,condition_name[0])) for bdc in subj_wave_behavioral_data.condition]

            # #get inclusive or of the two boolean lists
            # condition_match = [x or y for x,y in zip(condition_match_1,condition_match_2)]
            # #now get inclusive list of each trial preceding and following each value in condition_match
            # #first, get the indices of the True values in condition_match
            # condition_match_indices = [i for i, x in enumerate(condition_match) if x]
            # #now get the indices of the trials before and after each of these
            # condition_match_indices_wider_nested = [[i-2,i-1,i,i+1,i+2] for i in condition_match_indices]
            # #now flatten this list, removed duplicates, and sort it
            # condition_match_indices_wider = sorted(list(set([item for sublist in condition_match_indices_wider_nested for item in sublist])))
            
            
            # #now let's visualize the matching conditions alongside the design file data associated with this condition
            # #alongside the tw oconditions before or after it
            # #select rows from the behavioral data that match the condition
            # match_capped = min(20,len(condition_match_indices_wider))
            # print(subj_wave_behavioral_data.iloc[condition_match_indices_wider[0:match_capped]][['trial_n','go_no_go_condition','condition','onset','trial_duration']])
            # #now, for comparison, print the data we have in the design file
            # print(mat_dict['onsets'][0][condition_i])
            #that doesn't necessarily tell me what I want to know because there are too conditions matching the text
            #so let's try matching the onsets
            matching_onsets = [bd_onset in np.round(mat_dict['onsets'][0][condition_i],1) for bd_onset in np.round(subj_wave_behavioral_data.onset,1)] 
            onset_match_indices = [i for i, x in enumerate(matching_onsets) if x]
            onset_match_indices_wider_nested = [[i-2,i-1,i,i+1,i+2] for i in onset_match_indices]
            onset_match_indices_wider = sorted(list(set([item for sublist in onset_match_indices_wider_nested for item in sublist])))
            match_capped = min(20,len(onset_match_indices_wider))
            print(subj_wave_behavioral_data.iloc[onset_match_indices_wider[0:20]][['trial_n','go_no_go_condition','condition','onset','trial_duration']])
            print(mat_dict['onsets'][0][condition_i])


            #now match the raw raw data
            #first, get the raw data for this subject and wave
            #load mat file from the raw data
            #get a matching raw data file
            this_raw_file_pattern = raw_file_pattern.replace("DEVID","DEV" + subject_id).replace("RUNID",str(wave_number))
            matching_raw_file = [m for m in [re.search(this_raw_file_pattern, str(rf.name)) for rf in raw_files] if m is not None][0][0]

            raw_mat_dict = scipy.io.loadmat(str(sst_raw_data_path +"/"+ matching_raw_file), appendmat=False)
            raw_Seeker = raw_mat_dict['Seeker']
                        #             % The first column is trial number;
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
            seeker_df = pd.DataFrame(raw_mat_dict['Seeker'],columns=
            ['trial_n','numchunks','go_no_go','left_right','ladder','ladder_value','subject_response','ladder_movement',
            'reaction_time','actual_SSD','actual_SSD_plus_command_time','absolute_time','time_elapsed',
            'actual_SSD_error_check','trial_duration','time_course','UvH'])
            
            #great; now print the same rows as above, but from the raw data
            print(seeker_df.iloc[onset_match_indices_wider[0:match_capped]][['trial_n','absolute_time','time_elapsed', 'go_no_go','subject_response']])
            print("go_no_go value counts; use this to interpret the go_no_go column. Cue trials are the most common, followed by Go trials, then NoGo trials")
            print(seeker_df.go_no_go.value_counts())
            print("going to next condition")
            



            
            
            

            