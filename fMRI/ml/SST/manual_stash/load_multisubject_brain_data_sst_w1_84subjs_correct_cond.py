import sys
import os
import pandas as pd

sys.path.append(os.path.abspath("../../ml/"))

from dev_wtp_io_utils import *

nonbids_data_path = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/"
ml_data_folderpath = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/ml"

#test_train_df_raw = pd.read_csv(nonbids_data_path + "fMRI/ml/train_test_markers_20210601T183243.csv")
test_train_df_raw = pd.read_csv(nonbids_data_path + "fMRI/ml/train_test_markers_20211027T173724.csv")


include_exclude_list = pd.read_csv("../nsc_subject_exclusions.csv")


test_train_df_raw = test_train_df_raw.merge(
    include_exclude_list[include_exclude_list.Task=='SST'],left_on='sub_label',right_on='SubjectId',how='left')
test_train_df_raw.loc[test_train_df_raw.Include.isna(),'Include'] = True
test_train_df = test_train_df_raw[test_train_df_raw.Include==True]

exclude_subjects = ['DEV061','DEV185','DEV187','DEV189','DEV190','DEV192','DEV198','DEV203','DEV220','DEV221']


train_subjs = test_train_df.loc[test_train_df.SplitGroup=='Train','sub_label'].tolist()#only get the train subjects; ignore those previously marked hold-out

def get_Brain_Data_for_sub(sub_label, behavdesign, betaseries_path = '/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/SST/wave1/betaseries/'):
    return(dev_wtp_io_utils.get_Brain_Data_betas_for_sub(sub_label,behavdesign,betaseries_path))

from dev_wtp_io_utils import import_sst_betaseries_w1_subjs_to_pkl


all_sst_events= pd.read_csv(ml_data_folderpath +"/SST/" + "all_sst_events.csv")
#cut out other waves
sst_1_behavdesign_1 = all_sst_events[(all_sst_events.wave=='wave1')].reset_index(drop=True)
#label the ITI as such
sst_1_behavdesign_1.loc[(all_sst_events.trial_type.isna()),'trial_type']='ITI'
#ensure it is correctly ordered
sst_1_behavdesign_clean = sst_1_behavdesign_1.sort_values(['subject','onset']).reset_index(drop=True)
#now tell it the name of the corresponding beta. this is easy; they are all consecutive
sst_1_behavdesign_clean['beta'] = 'beta_' + (sst_1_behavdesign_clean.groupby(['subject','wave']).cumcount()+1).astype(str).apply(lambda x: x.zfill(4)) + '.nii'

sst_1_behavdesign_correct_conditions=sst_1_behavdesign_clean[sst_1_behavdesign_clean.trial_type.isin(['correct-go','correct-stop'])]

print(sst_1_behavdesign_correct_conditions.trial_type.value_counts())


#we have data missing fro mthese subjects below. not enstirely sure yet; see 
#https://docs.google.com/document/d/1EB0ACA6qhMkDEgv-zqNTepPCe_x41fRQHaeqT47vazM/edit#heading=h.60rb13rlxkrq


train_subjs_selected = [ts for ts in train_subjs if (ts not in exclude_subjects)]

import_sst_betaseries_w1_subjs_to_pkl(
    train_subjs_selected,'betaseries',
    behavioral_design=sst_1_behavdesign_correct_conditions,
    out_folder = ml_data_folderpath + "/SST/",
out_file_suffix = '_correct_cond')