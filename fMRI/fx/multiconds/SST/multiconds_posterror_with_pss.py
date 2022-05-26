import argparse
import json
import re
from os import PathLike
from pathlib import Path
from typing import Union, List

import numpy as np
from numpy.core.records import fromarrays # https://stackoverflow.com/questions/33212855/how-can-i-create-a-matlab-struct-array-from-scipy-io
import scipy.io
from zmq import PROTOCOL_ERROR_ZMTP_MALFORMED_COMMAND_MESSAGE
from multiconds import *

def create_pss_parametric_modulator_struct(pss_list:List,posterror_masks_dict : dict,posterror_conditions: dict):
    posterror_names = posterror_conditions['names']
    pmod_list = []

    def create_pss_parametric_modulator_struct(mod_values,condition_name):
        if np.any(mod_values is not None):
            #condition_column = condition_mask*reaction_time
            #I'm unsure we should be mean-centering by condition here rather than across all reaction times, but it seems probably the right thing to do?

            #because we don't have a pss for every value
            #hmmm, what were we doing before? in the "rt" version, there wasn't a post-error reaction time for every single thing
            #I think we were doing reaction times of post-error values...which makes sense.
            #need to think carefully, then:
            #(1) how do we arrange the conditions so that we can do the parametric modulation, and
                    # we might be able to keep the conditions the same, and just set blank parametric mod trials to 0, following the mean-centering
                    # I think that makes sense?
                    # maybe not perfect but perhaps close enough
                    # actually, think that moving the trials into another condition within the task is not really going to help us explain the variance any better.
            #(2) are we meaning to pick the failed stop trials, the correct stop trials, or the trials immediately following them?
                # it is the trials immediately following them. need to make sure that's what we're doing.
            condition_column = mod_values - np.nanmean([m for m in mod_values])
            condition_column[np.isnan(condition_column)]=0
            if condition_column is None:
                return None
            else:
                #TO DO; SEE: https://stackoverflow.com/questions/19797822/creating-matlab-cell-arrays-in-python
                #THINK THAT IS THE SOLUTION.
                condition_column_npt = np.empty(1,dtype='O')
                condition_column_npt[0] = condition_column

            caps = re.findall("[A-Z]",condition_name)
            abbreviation = "".join(caps).lower()
            abbreviation = abbreviation[0].upper() + abbreviation[1:]
            pmod_item = (
                abbreviation + "RT",
                condition_column_npt,
                [1.0]
            )

            return(pmod_item)
            #pmod_list = pmod_list + [pmod_item]
        else:
            #raise Exception("need to verify the next level is prepped to deal with some subjects having a missing regressor.")
            warnings.warn(
                "need to verify the next level is prepped to deal with some subjects having a missing regressor for condition " + condition_name + ".")
            return(None)

    pmod_list = pmod_list + [create_pss_parametric_modulator_struct(pss_list['CorrectGoFollowingCorrectStop'],'CorrectGoFollowingCorrectStop')]
    pmod_list = pmod_list + [create_pss_parametric_modulator_struct(pss_list['CorrectGoFollowingFailedStop'], 'CorrectGoFollowingFailedStop')]
    #this only works if these items are at the start of the list. if they aren't, we have a problem to deal with.
    if 'CorrectGoFollowingCorrectStop' in posterror_names and posterror_names[0]!='CorrectGoFollowingCorrectStop':
        raise Exception('CorrectGoFollowingCorrectStop not where expected.')
    if 'CorrectGoFollowingFailedStop' in posterror_names and 'CorrectGoFollowingFailedStop' not in posterror_names[0:2]:
        raise Exception('CorrectGoFollowingFailedStop not where expected.')

    pmod_list = [pmod for pmod in pmod_list if pmod_list is not None]

    if len(pmod_list)==0:
        return({}) #return nothing because there doesn't appear to be any params to pass

    pmod_array = np.array(
        pmod_list,
        dtype=([('name','object',(1,)),('param','O',(1,)),('poly','object',(1,))])
    )

    
    #return({'R':duration_array,'names':name_list})
    #above design was passing duration as a [multiple] regressor, when in fact, we need it as a parametric modulator.
    return({
        'pmod': pmod_array,
        'orth': np.array([0]*len(pmod_list),dtype='O')
    })

##NEXT TO DO: HOOK THIS UP AND RUN IT; IF IT RUNS, WRITE OUTPUT TO MAT FILES; IF IT DOESN'T, WORK OUT HOW TO DEAL WITH THE MISSING REGRESSOR ISSUE.


def main(input_dir: str, bids_dir: str = None, file_limit=None,
         use_rt_for_go_success_trials=True,
         output_folder=""):
    print(input_dir)
    folder_id = 'posterror_conditions_w_pss'

    files = list(Path(input_dir).glob('DEV*.mat'))
    files.sort()
    pattern = 'DEV(\\d{3})_run(\\d{1})_.*.mat'
    # pattern = 'DEV(\\d{3})_(\\d{1})_SST1\\.mat'

    # for testing
    if file_limit is not None:
        files = files[0:file_limit]

    file_condition_index = {}
    file_condition_index['base'] = {}
    file_condition_index['posterror'] = {}
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
            posterror_masks_dict = create_posterror_masks_from_masks(masks)
            posterror_masks = list(posterror_masks_dict.values())
            print_mask_signature(posterror_masks)

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
                # trials = create_trials(trial_number, trial_start_time, trial_duration, subject_response)

                # Create paths and file names
                # write_betaseries(output_folder, subject_id, wave_number, trials)

                pss_set = get_pss(masks,posterror_masks_dict, reaction_time)
                #identify each error event
                #look up the previous go trial
                #look up the next

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
                    'arrow_presented': arrow_presented,
                    'pss': pss_set['by_trial']})

                multicond_df_list = multicond_df_list + [trial_df_row]

                posterror_conditions = create_posterror_conditions(
                    trial_start_time, trial_duration, posterror_masks)


                posterror_reaction_times = create_pss_parametric_modulator_struct(
                    pss_set['by_poststop_trial_type'],posterror_masks_dict,posterror_conditions)

                posterror_conditions.update(posterror_reaction_times)

                write_beta_data(output_folder, folder_id, subject_id, wave_number, posterror_conditions)

                file_condition_index['posterror'][(subject_id,wave_number)] = posterror_conditions['names']

                print("written data for subject " + str(subject_id))
        else:
            print("match not found for " + str(f.name))

    print("creating a complete list of the data with durations and reaction times...")
    multicond_df = pd.concat(multicond_df_list)
    multicond_df.to_csv(output_folder + folder_id + "_multicond_out.csv")

    print("creating a list of each file with the set of conditions within that file...")
    save_varying_condition_list(output_folder = output_folder,
                            subfolder = folder_id,
                            file_condition_dict = file_condition_index['posterror'],
                            target_conditions = ['CorrectGoFollowingCorrectStop', 'CorrectGoFollowingFailedStop'])





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

    

    #we don't do BIDs here because BIDs, by convention, uses RT for duration.
    main(args.input_dir, bids_dir=None, use_rt_for_go_success_trials=False, output_folder= args.output_dir)
