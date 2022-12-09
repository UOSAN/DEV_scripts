import argparse
import json
import re
from os import PathLike
from pathlib import Path
from typing import Union, List

import numpy
import scipy.io
from multiconds import *
from multiconds_utils import *



def main(input_dir: str, bids_dir: str = None, file_limit=None,
         use_rt_for_go_success_trials=True,
         output_folder="",
         preprocessed_data_filepath: str = None,
         folder_id: str = 'posterror_w_post_pre',
         include_parametric_modulators: bool = True):
    print(input_dir)

    files = list(Path(input_dir).glob('DEV*.mat'))
    files.sort()
    pattern = 'DEV(\\d{3})_run(\\d{1})_.*.mat'
    # pattern = 'DEV(\\d{3})_(\\d{1})_SST1\\.mat'

    # for testing
    if file_limit is not None:
        files = files[0:file_limit]

    file_condition_index = {}
    file_condition_index['posterror_conditions'] = {}
    multicond_df_list = []

    preprocessed_behavioral_data = pd.read_csv(preprocessed_data_filepath)

    #it's probably already sorted, but just to make absolutely sure, because we might rely on this.
    preprocessed_behavioral_data.sort_values(['subid','waveid','trial_n'],inplace=True)
    #drop sub 999 because it's test data and causes errors at this stage.
    preprocessed_behavioral_data = preprocessed_behavioral_data.loc[preprocessed_behavioral_data.subid!=999,:]
    

    for f in files:
        match = re.search(pattern, str(f.name))
        if match:
            subject_id, wave_number = match.groups()
            print(f.name)
            if subject_id=='999':
                continue

            if int(wave_number)>2:
                continue
                #no need to get the third wave data because there is no fMRI data for it.
            

            matching_preprocessed_behavioral_data = preprocessed_behavioral_data.loc[
                (preprocessed_behavioral_data.subid==('DEV' + subject_id)) & (preprocessed_behavioral_data.waveid==int(wave_number))
                ,:
            ]

            # Read data out of the .mat file
            trial_number, go_no_go_condition, subject_response, reaction_time, trial_duration, trial_start_time, arrow_presented = \
                read_data(f, use_rt_for_go_success_trials=use_rt_for_go_success_trials)

            # Create masks for the various conditions
            #create masks uses a hard-coded list of conditions, so we need not that next to it.
            masks = create_masks(go_no_go_condition, subject_response)
            mask_names = ['correct-go', 'correct-stop', 'failed-stop', 'null', 'failed-go']
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
                trial_type_names = mask_names
                for mask, name in zip(masks, trial_type_names):
                    np.putmask(trial_type, mask, name)
                write_bids_events(bids_dir, subject_id, wave_number,
                                  np.stack(
                                      (trial_start_time, trial_duration, trial_type, arrow_presented,
                                       cleaned_subject_response), axis=1))
            else:
                print("creating betaseries and conditions")
                # create onset files for SPM first-level analysis
                #trials = create_trials(trial_number, trial_start_time, trial_duration, subject_response)

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

                posterror_conditions = create_conditions(trial_start_time, trial_duration, list(posterror_masks_dict.values()), list(posterror_masks_dict.keys()))

                if len(masks)!=len(posterror_conditions['names']):
                    print('masks and conditions do not match')
                    #print(masks)
                    #print(conditions['names'])
                    print([sum(ms) for ms in masks])
                    print("that's the match")
                    #continue
                
                if include_parametric_modulators:
                    # pes = get_pes(masks,reaction_time)
                    #identify each error event
                    #look up the previous go trial
                    #look up the next
                    modulator_var = matching_preprocessed_behavioral_data['next_last_rt_change'].values
                    modulator_var[np.isnan(modulator_var)] = 0.0

                    modulator_struct = create_parametric_modulator_struct(
                        modulator_var,
                        #just get the conditions that we actually have for this subject :-)
                        [posterror_masks_dict[pem_k] for pem_k in posterror_masks_dict if pem_k in posterror_conditions['names']],
                        posterror_conditions,
                        modulator_suffix='_post_current_drt')

                    posterror_conditions.update(modulator_struct)

                write_beta_data(output_folder, folder_id, subject_id, wave_number, posterror_conditions)

                file_condition_index['posterror_conditions'][(subject_id,wave_number)] = posterror_conditions['names']

                print("written data for subject " + str(subject_id))
        else:
            print("match not found for " + str(f.name))

    print("creating a complete list of the data with durations and reaction times...")
    multicond_df = pd.concat(multicond_df_list)
    multicond_df.to_csv(output_folder + folder_id + "_multicond_out.csv")

    print("creating a list of each file with the set of conditions within that file...")
    save_varying_condition_list(output_folder = output_folder,
                            subfolder = folder_id,
                            file_condition_dict = file_condition_index['posterror_conditions'],
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

    parser.add_argument('-s', '--supplemental', metavar='supplemental data', action='store',
                        type=str, required=False, default=None,
                        help='absolute or relative path for output',
                        dest='supplemental_data'
                        )

    args = parser.parse_args()

    print(args.input_dir)

    #we don't do BIDs here because BIDs, by convention, uses RT for duration.
    main(args.input_dir, 
    bids_dir=None, 
    use_rt_for_go_success_trials=False, 
    output_folder= args.output_dir,
    preprocessed_data_filepath = args.supplemental_data,
    folder_id='posterror_conditions_w_drt',
    include_parametric_modulators=True
    )
