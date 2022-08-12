#!/usr/bin/env python3

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
import sys

print("extracting raw data")
sys.stdout.flush()

#get the behavioral data and the list of subjects allocated for training
wtpw1_behavdesign_clean = pd.read_csv("../data/wtpw1_behavdesign_clean.csv")
test_train_df = pd.read_csv("../data/train_test_markers_20210601T183243.csv")
train_subjs = test_train_df.loc[test_train_df.SplitGroup=='Train','sub_label'].tolist()

training_Brain_Data = dev_wtp_io_utils.get_event_related_Brain_Data_for_all_subs_all_runs_fast(train_subjs[0:6],1,wtpw1_behavdesign_clean)

with open('../data/Brain_Data_raw_6subs.pkl', 'wb') as pkl_file:
    pickle.dump(training_Brain_Data,pkl_file)