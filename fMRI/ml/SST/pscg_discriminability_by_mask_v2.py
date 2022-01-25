print("starting...")
#designed to be batched, this runs the discriminability pipeline for a SPECIFIC mask 
#this file measures post-stop, correct-go and is built based on sst_discriminability_by_mask.py
from discriminability_tools import *

import pickle
from IPython.core.display import display, HTML, Markdown
from nilearn.decoding import Decoder
from sklearn.model_selection import StratifiedKFold
from random import randint
import math

import sys
import os
import pandas as pd
import gc

# print(sys.argv)
# for item in sys.argv:
#     print(item)

print(sys.argv[1])

print(sys.argv[2])

# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("-m","--maskpath",
#                     help="the mask path (use double quotes if necessary)",
#                     type=str)

# args = parser.parse_args()

# print("arg pass maskpath is: " + args.maskpath)


sys.path.append(os.path.abspath("../../ml/"))

from apply_loocv_and_save import *
from dev_wtp_io_utils import *
import gc
import nibabel as nib

from os import path
import multiprocessing
import math





nonbids_data_path = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/"
ml_data_folderpath = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/ml"
train_test_markers_filepath = ml_data_folderpath + "/train_test_markers_20210601T183243.csv"
test_train_df = pd.read_csv(train_test_markers_filepath)

all_sst_events= pd.read_csv(ml_data_folderpath +"/SST/" + "all_sst_events.csv")


dataset_name = 'conditions'

from nilearn.decoding import DecoderRegressor, Decoder

script_path = '/gpfs/projects/sanlab/shared/DEV/DEV_scripts/fMRI/ml'

def pscg_resp_trans_func(X):
    return(X.post_stop_correct_go_subtype)


#cpus_available = int(os.getenv('CPUS_PER_TASK'))

#custom thing I have set in my jupyter notebook task.
cpus_available = multiprocessing.cpu_count()

cpus_to_use = min(cpus_available-1,math.floor(0.9*cpus_available))
print(cpus_available, cpus_to_use)

brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_betaseries_84subs_poststop_correctgo.pkl'
#brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_betaseries_84subs_correct_cond.pkl'
#brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_betaseries_58subs_correct_cond.pkl'
#brain_data_filepath = ml_data_folderpath + '/SST/Brain_Data_conditions_43subs_correct_cond.pkl'

## get subject IDs in the dataset

all_subjects = load_and_preprocess(
    brain_data_filepath,
    train_test_markers_filepath,
    subjs_to_use = None,
    response_transform_func = pscg_resp_trans_func,
    clean=None)

all_subjects['groups']

subj_list = np.unique(all_subjects['groups'])

del all_subjects
gc.collect()

summary_results_list = {}
discriminability_version_id= "pscg_v_2"

#now dow the main loop
#have to do it twice becuase we have different masks which require different thresholds.
mask_filepath = sys.argv[1]
mask_threshold = float(sys.argv[2])
print('mask threshold: ' + str(mask_threshold))
if (mask_threshold!=0) & (mask_threshold!=30):
    raise Exception("v2 discriminability uses mask threshold=30 for harvard-oxford masks, but a different threshold was set.")


mask_filename = os.path.basename(mask_filepath)
mask_name = mask_filename.split(".")[0]

print("## " + mask_name)
print(mask_filepath)
print('mask threshold: ' + str(mask_threshold))
mask_img = create_mask_from_images([mask_filepath],threshold=mask_threshold)


run_desc = discriminability_version_id + "_" + mask_name
#get the results
summary_results = get_all_subjs_discriminability_masked(
    subj_list, run_desc,ml_data_folderpath=ml_data_folderpath,
    subject_discrim_args = 
    {'train_test_markers_filepath':train_test_markers_filepath, 
     'brain_data_filepath':brain_data_filepath, 
     'resp_trans_func': pscg_resp_trans_func,
     'mask':mask_img,
     'splits_to_use': "min_class"
    })

summary_results['mask_threshold']=mask_threshold

with open(
    ml_data_folderpath + "/SST/discriminability_by_mask_" + 
    discriminability_version_id + "_" + mask_name + ".pkl", 'wb') as handle:
    pickle.dump(summary_results,handle)


   