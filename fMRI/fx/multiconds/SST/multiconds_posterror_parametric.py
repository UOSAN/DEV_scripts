import argparse
import json
import re
from os import PathLike
from pathlib import Path
from typing import Union, List

import numpy
import scipy.io
from multiconds import *

raise Exception("I believe this is deprecated; it seems to implement posterror_with_durations by another way, but incomplete.")
def create_duration_multiple_regressor_df(reaction_time,posterror_masks,posterror_conditions):
    posterror_names = posterror_conditions['names']
    duration_array = None
    name_list = []
    for condition_i, condition_name in enumerate(posterror_names):
        condition_mask = posterror_masks[condition_i]
        #look up to see if we should include this regressor at all; it should
        if sum(condition_mask)>0:
            # print(str(condition_i) + ": " + posterror_names[condition_i])
            # print(len(condition_mask))
            condition_column = condition_mask*reaction_time
            # print(condition_column)
            if duration_array is None:
                duration_array = numpy.array([condition_column]).T
            else:
                # print("duration_rray:")
                # print(duration_array.shape)
                # print(condition_column.shape)
                duration_array = numpy.append(duration_array, numpy.array([condition_column]).T, axis=1)

            name_list = name_list + [posterror_names[condition_i]]
        else:
            #raise Exception("need to verify the next level is prepped to deal with some subjects having a missing regressor.")
            warnings.warn(
                "need to verify the next level is prepped to deal with some subjects having a missing regressor for condition " + condition_name + ".")

    return({'R':duration_array,'names':name_list})

##NEXT TO DO: HOOK THIS UP AND RUN IT; IF IT RUNS, WRITE OUTPUT TO MAT FILES; IF IT DOESN'T, WORK OUT HOW TO DEAL WITH THE MISSING REGRESSOR ISSUE.


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
            posterror_masks = create_posterror_masks_from_masks(masks)
            print_mask_signature(posterror_masks)

            # Perform some quality checking on the numbers of responses (should be 256),
            # the number of null trials (should be 128),
            # go trials (should be 96), and no-go trials (should be 32)
            if subject_response.size != COUNT_RESPONSE:
                print(f'Wrong number of responses   : (subject, expected, actual) '
                      f'({subject_id}, {COUNT_RESPONSE}, {subject_response.size})')
            if numpy.count_nonzero(masks[0] + masks[-1]) != COUNT_GO:
                print(f'Wrong number of go trials : (subject, run, expected, actual) '
                      f'({subject_id}, {wave_number}, {COUNT_GO}, {numpy.count_nonzero(masks[0] + masks[-1])})')
            if numpy.count_nonzero(masks[1] + masks[2]) != COUNT_NO_GO:
                print(f'Wrong number of no-go trials: (subject, expected, actual) '
                      f'({subject_id}, {COUNT_NO_GO}, {numpy.count_nonzero(masks[1] + masks[2])})')
            if numpy.count_nonzero(masks[3]) != COUNT_NULL:
                print(f'Wrong number of null trials : (subject, expected, actual) '
                      f'({subject_id}, {COUNT_NULL}, {numpy.count_nonzero(masks[3])})')

            # preprocess subject responses for attention check
            cleaned_subject_response = clean_response_data(subject_response, arrow_presented)

            if bids_dir:  # create MAT files storing behavioral information in bids format
                print("creating bids events")
                trial_type = numpy.empty_like(trial_number, dtype=numpy.object)
                trial_type_names = ['correct-go', 'correct-stop', 'failed-stop', 'null', 'failed-go']
                for mask, name in zip(masks, trial_type_names):
                    numpy.putmask(trial_type, mask, name)
                write_bids_events(bids_dir, subject_id, wave_number,
                                  numpy.stack(
                                      (trial_start_time, trial_duration, trial_type, arrow_presented,
                                       cleaned_subject_response), axis=1))
            else:
                print("creating betaseries and conditions")
                # create onset files for SPM first-level analysis
                # trials = create_trials(trial_number, trial_start_time, trial_duration, subject_response)

                # Create paths and file names
                # write_betaseries(output_folder, subject_id, wave_number, trials)

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
                    'arrow_presented': arrow_presented})

                multicond_df_list = multicond_df_list + [trial_df_row]

                posterror_conditions = create_posterror_conditions(
                    trial_start_time, trial_duration, posterror_masks)
                write_beta_data(output_folder, 'posterror_conditions', subject_id, wave_number, posterror_conditions)

                posterror_reaction_times = create_duration_multiple_regressor_df(
                    reaction_time,posterror_masks,posterror_conditions)

                file_condition_index['posterror'][(subject_id,wave_number)] = posterror_conditions['names']

                if posterror_reaction_times['R'] is not None:
                    write_beta_data(output_folder, 'posterror_reaction_times',subject_id,wave_number,
                                    posterror_reaction_times)

                print("written data for subject " + str(subject_id))
        else:
            print("match not found for " + str(f.name))

    print("creating a complete list of the data with durations and reaction times...")
    multicond_df = pd.concat(multicond_df_list)
    multicond_df.to_csv(output_folder + "posterror_multicond_out.csv")

    print("creating a list of each file with the set of conditions within that file...")
    save_varying_condition_list(output_folder = output_folder,
                            subfolder = "posterror_conditions",
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

