import math
import pandas as pd
import numpy as np
import os
import nltools as nlt
import nilearn as nil
import nibabel as nib
import warnings
import glob
import random
import pickle
from operator import itemgetter
import dev_wtp_io_utils

#get the cleaned behavioral data and the list of subjects allocated for training
wtpw1_behavdesign_clean = pd.read_csv("../data/wtpw1_behavdesign_clean.csv")
test_train_df = pd.read_csv("../data/train_test_markers_20210601T183243.csv")
train_subjs = test_train_df.loc[test_train_df.SplitGroup=='Train','sub_label'].tolist()

#that data doesn't include the event_stage data, so let's get that and merge it in.
behavioral_data_path = '/gpfs/projects/sanlab/shared/DEV/nonbids_data/Tasks/WTP/output/'
[run_list, run_event_df_list, run_event_stage_df_list] = dev_wtp_io_utils.get_comprehensive_run_data_from_mat_dir(behavioral_data_path)
del run_event_df_list
event_data_to_use = wtpw1_behavdesign_clean.loc[
    :,['event_id','run','wave','subject','liking_rating','response']
                                                ]
event_stage_df_clean = event_data_to_use.merge(
         run_event_stage_df_list,
    how='left')   


#now run the code specifically to grab the choice events
events_choice_period = event_stage_df_clean[event_stage_df_clean.stage=='bid_prechoice']



training_Brain_Data_60 = dev_wtp_io_utils.get_event_related_Brain_Data_for_all_subs_all_runs_fast(train_subjs,1,events_choice_period)

with open('../data/Brain_Data_raw_fingerpress_60subjs.pkl', 'wb') as pkl_file:
    pickle.dump(training_Brain_Data_60,pkl_file)