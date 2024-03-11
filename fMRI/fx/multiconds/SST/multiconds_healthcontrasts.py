import argparse
from collections import OrderedDict
import json
import re
from os import PathLike
from pathlib import Path
from typing import Union, List
import numpy as np

import scipy.io
from multiconds import *



# def get_condition_mask_dict(condition_masks: List,health_data: List) -> List:
#     """create masks based on original masks, but with health data"""
        
#     go_success = condition_masks[0]
#     no_go_success = condition_masks[1]
#     no_go_fail = condition_masks[2]
#     null_trials = condition_masks[3]
#     go_fail = condition_masks[4]


#     dict_list = []
#     for hc_i in [HEALTHY_TRIAL, UNHEALTHY_TRIAL]:
#         if hc_i == HEALTHY_TRIAL:
#             hc = 'Healthy'
#         elif hc_i == UNHEALTHY_TRIAL:
#             hc = 'Unhealthy'

#         hc_od = OrderedDict({
#             hc + 'CorrectGo': go_success & (health_data==hc_i),
#             hc + 'CorrectStop': no_go_success & (health_data==hc_i),
#             hc + 'FailedGo': go_fail & (health_data==hc_i),
#             hc + 'FailedStop': no_go_fail & (health_data==hc_i),
#             hc + 'Cue': null_trials & (health_data==hc_i)

#         })
        
#         dict_list = dict_list + [hc_od]

#     #combine the two ordered dictionaries
#     return(OrderedDict(**dict_list[0],**dict_list[1]))



def create_health_masks_from_mask_dict(condition_masks: OrderedDict,health_data: List) -> List:
    """create masks based on original masks, but with health data"""
        

    dict_list = []
    for hc_i in [HEALTHY_TRIAL, UNHEALTHY_TRIAL, HEALTH_STATUS_NULL]:
        if hc_i == HEALTHY_TRIAL:
            hc = 'Healthy'
        elif hc_i == UNHEALTHY_TRIAL:
            hc = 'Unhealthy'
        elif hc_i == HEALTH_STATUS_NULL:
            hc = 'Null'

        hc_od = OrderedDict({})
        for k,v in condition_masks.items():
            if ((hc_i==HEALTH_STATUS_NULL) == (k=='Cue')):
                #i.e., if we're looking at the cue and the health status is null, or if we're looking at a non-cue and the health status is not null
                hc_od[hc +"_" + k] = v & (health_data==hc_i)
        
        dict_list = dict_list + [hc_od]

    #combine the two ordered dictionaries
    return(OrderedDict(**dict_list[0],**dict_list[1],**dict_list[2]))


def create_health_conditions(start_time: np.ndarray, duration: np.ndarray, health_cond_masks: OrderedDict):
    condition_labels = list(health_cond_masks.keys())
    return (create_conditions(start_time, duration, list(health_cond_masks.values()), condition_labels=condition_labels))

#def create_health_conditions():



def main(input_dir: str, bids_dir: str = None, file_limit=None,
         use_rt_for_go_success_trials=True,
         include_rt_pmod=True,
         folder_id='conditions_health',
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
    file_condition_index['base'] = {}
    file_condition_index['health'] = {}
    multicond_df_list = []


    for f in files:
        match = re.search(pattern, str(f.name))
        if match:
            subject_id, wave_number = match.groups()
            print(f.name)

            # Read data out of the .mat file
            trial_number, go_no_go_condition, subject_response, reaction_time, trial_duration, trial_start_time, arrow_presented, health_status = \
                read_data(f, use_rt_for_go_success_trials=use_rt_for_go_success_trials,include_health=True)

            # Create masks for the various conditions
            masks_dict = create_masks_dict(go_no_go_condition, subject_response)
            print_mask_signature(masks_dict)
            quality_check(subject_response,subject_id,list(masks_dict.values()),wave_number)

            masks_go_no_go_dict = get_go_no_go_masks(masks_dict)
            print_mask_signature(masks_go_no_go_dict)
            
            # create masks for the post-error slowing
            health_masks_8c_dict = create_health_masks_from_mask_dict(masks_dict, health_status)
            health_masks_8c = list(health_masks_8c_dict.values())
            print_mask_signature(health_masks_8c_dict)

            # create masks for the post-error slowing
            health_masks_4c_dict = create_health_masks_from_mask_dict(masks_go_no_go_dict, health_status)
            health_masks_4c = list(health_masks_4c_dict.values())
            print_mask_signature(health_masks_4c_dict)

            
            
            # preprocess subject responses for attention check
            cleaned_subject_response = clean_response_data(subject_response, arrow_presented)

            if bids_dir:  # create MAT files storing behavioral information in bids format
                raise NotImplementedError("BIDS not implemented yet")
            
            else:
                print("creating betaseries and conditions")
                # create onset files for SPM first-level analysis
                # conditions = create_conditions(trial_start_time, trial_duration, masks)
                # write_beta_data(output_folder, 'conditions', subject_id, wave_number, conditions)
                trial_df_row = pd.DataFrame({
                    'subject_id':subject_id,
                    'wave_number':wave_number,
                    'trial_number': trial_number, 
                    'go_no_go_condition': go_no_go_condition, 
                    'subject_response': subject_response, 
                    'reaction_time': reaction_time,
                    'trial_duration': trial_duration, 
                    'trial_start_time': trial_start_time, 
                    'arrow_presented': arrow_presented
                    })

                multicond_df_list = multicond_df_list + [trial_df_row]

                health_conditions_8c = create_health_conditions(
                    trial_start_time, trial_duration, health_masks_8c_dict)
                write_beta_data(output_folder, folder_id, subject_id, wave_number, health_conditions_8c)
                file_condition_index['health'][(subject_id,wave_number)] = health_conditions_8c['names']

                #extra set where we don't have a distinction between failed and correct
                health_conditions_4c = create_health_conditions(
                    trial_start_time, trial_duration, health_masks_4c_dict)
                write_beta_data(output_folder, folder_id + "_gng", subject_id, wave_number, health_conditions_4c)

                print("written data for subject " + str(subject_id))
        else:
            print("match not found for " + str(f.name))

    print("creating a complete list of the data with durations and reaction times...")
    multicond_df = pd.concat(multicond_df_list)
    multicond_df.to_csv(output_folder + folder_id + "_multicond_out.csv")

    # print("creating a list of each file with the set of conditions within that file...")
    # save_varying_condition_list(output_folder = output_folder,
    #                         subfolder = folder_id,
    #                         file_condition_dict = file_condition_index['posterror'],
    #                         target_conditions = ['CorrectGoFollowingCorrectStop', 'CorrectGoFollowingFailedStop'])



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

    parser.add_argument('-o', '--output', metavar='directory for output', action='store',
                        type=str, required=False, default=None,
                        help='absolute or relative path for output',
                        dest='output_dir'
                        )

    args = parser.parse_args()

    print(args.input_dir)

    #we don't do BIDs here because BIDs, by convention, uses RT for duration.
    main(args.input_dir, bids_dir=None, use_rt_for_go_success_trials=False, output_folder= args.output_dir)
