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

def create_rt_parametric_modulator_struct(reaction_time,posterror_masks,posterror_conditions):
    posterror_names = posterror_conditions['names']
    duration_array = None
    pmod_list = []
    # pmod_dict = {}
    # for k in ['name','param','poly']:
    #     pmod_dict[k] = []
    
    for condition_i, condition_name in enumerate(posterror_names):
        condition_mask = posterror_masks[condition_i]
        #look up to see if we should include this regressor at all; it should
        if sum(condition_mask)>0:
            # print(str(condition_i) + ": " + posterror_names[condition_i])
            # print(len(condition_mask))
            #condition_column = condition_mask*reaction_time
            #I'm unsure we should be mean-centering by condition here rather than across all reaction times, but it seems probably the right thing to do?
            condition_column = reaction_time[condition_mask]-np.mean(reaction_time[condition_mask])
            # print(condition_column)
            if condition_column is None:
                continue
            else:
                # print("duration_rray:")
                # print(duration_array.shape)
                # print(condition_column.shape)
                #TO DO; SEE: https://stackoverflow.com/questions/19797822/creating-matlab-cell-arrays-in-python
                #THINK THAT IS THE SOLUTION.
                condition_column_npt = np.empty(1,dtype='O')
                condition_column_npt[0] = condition_column
                #condition_column_npt[0] ``= np.array([condition_column],dtype='O').T
                #condition_column_npt = np.array(np.array(condition_column).T,dtype=object)
                #rt_array = np.append(condition_column_npt, axis=1)

            #name_list = name_list + [posterror_names[condition_i]]
            # pmod_item = {
            #     'name':posterror_names[condition_i],
            #     'param':condition_column_npt,
            #     'poly':[]
            # }
            caps=re.findall("[A-Z]",posterror_names[condition_i])
            abbreviation="".join(caps).lower()
            abbreviation = abbreviation[0].upper() + abbreviation[1:]
            pmod_item = (
                abbreviation + "RT",
                condition_column_npt,
                [1.0]
            )
            # pmod_dict['name'] = pmod_dict['name'] + [posterror_names[condition_i]]
            # pmod_dict['param'] = pmod_dict['param'] + [condition_column]
            # pmod_dict['poly'] = pmod_dict['poly'] + [fromarrays([[]])]
            # pmod_item = [
            #     posterror_names[condition_i],
            #     condition_column_npt,
            #     []
            # ]
            pmod_list = pmod_list + [pmod_item]
        else:
            #raise Exception("need to verify the next level is prepped to deal with some subjects having a missing regressor.")
            warnings.warn(
                "need to verify the next level is prepped to deal with some subjects having a missing regressor for condition " + condition_name + ".")

    if len(pmod_list)==0:
        return({}) #return nothing because there doesn't appear to be any params to pass
    #pmod_rec_array = fromarrays(pmod_list,names=['name','param','poly'])
    # testrec = fromarrays([['hi', 'hello'], [np.array(2),np.array(1)],[3,30.]], names=['name', 'param','poly'])
    # testrec = fromarrays([
    #     ['hi', 'hello'], 
    #     [fromarrays([1,2]),fromarrays([1,2])]#,
    #     #[fromarrays([[]]),fromarrays([[]])]
    #     ], names=['name', 'param'])
    # scipy.io.savemat("testmat.mat",{'var1':testrec})

    # testrec = fromarrays([
    #     ['hi', 'hello'], 
    #     [([1,2]),fromarrays([1,2])]#,
    #     #[fromarrays([[]]),fromarrays([[]])]
    #     ], names=['name', 'param'])
    # scipy.io.savemat("testmat.mat",{'var1':testrec})
    # x = np.array([('Rex', 9, [],[1,2,3]), ('Fido', 3, [],[10,20,30])],
    #          dtype=[('name', '<U255'), ('age', 'int'), ('weight_measure', 'float',(0,)),('myarr','int',(3,))])
    # #pmod_list = list(pmod_dict.values())
    #param_max_len = max([p[1][0].shape[0] for p in pmod_list])
    #param_max_len = max([len(p[1]) for p in pmod_list])
    # pmod_array = np.array(
    #     pmod_list,
    #     dtype=([('name','<U255'),('param','float',(1,param_max_len)),('poly','float',(0,))])
    # )
    pmod_array = np.array(
        pmod_list,
        dtype=([('name','object',(1,)),('param','O',(1,)),('poly','object',(1,))])
    )
    # scipy.io.savemat("testmat.mat",{'var2':pmod_array})
    # example_pmod_from_matlab = scipy.io.loadmat("/Users/bensmith/Documents/data/DEV/nonbids_data/fMRI/fx/models/SST/example_pmod.mat")
    # example_pmod_from_matlab['pmod_spm_aim']['param'].shape
    # example_pmod_from_matlab['pmod_spm_aim']['param'][0,1].shape
    # example_pmod_from_matlab['pmod_spm_aim']['param'][0,1][0].shape
    # example_pmod_from_matlab['pmod_spm_aim']['param'][0,1][0][0].shape
    
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
    folder_id = 'posterror_conditions_w_rt'

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

                # posterror_conditions = create_posterror_conditions(
                #     trial_start_time, trial_duration, posterror_masks.values())
                posterror_conditions = create_conditions(
                    trial_start_time, trial_duration, list(posterror_masks.values()),
                    condition_labels=list(posterror_masks.keys())
                )

                #pes = get_pes(masks,reaction_time)
                #identify each error event
                #look up the previous go trial
                #look up the next

                posterror_reaction_times = create_rt_parametric_modulator_struct(
                    reaction_time,list(posterror_masks.values()),posterror_conditions)

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
