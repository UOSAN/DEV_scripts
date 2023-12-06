
from glob import glob
import re
from socket import gethostname
import json
import pandas as pd
from yaml import SafeLoader
import yaml
import paramiko
import numpy as np

def load_config(config_path = None):
    if config_path is None: config_path = 'config.yml'
    print(gethostname(),flush=True)
    # Open the file and load the file
    with open(config_path) as f:
        all_yaml = yaml.load(f, Loader=SafeLoader)
        if gethostname() in all_yaml.keys():
            config = all_yaml[gethostname()]
        else:
            config = all_yaml['default']
            
    print(config,flush=True)
    return(config)


def get_data_for_confirmed_task_session(
        beta_glob,
        nonbids_data_path,
        dropbox_datapath,
        ml_scripting_path,
        task='SST',
        subj_wave_inclusion = 'all'
        ):
    """
    Based on get_data_for_confirmed_train_subjs
    I've taken out the code to exclude subjects based on the train/test split because this is no longer relevant
    However, this now includes code to decide which group of subjects to examine: wave 1, wave 2, or both waves.
    subj_wave_inclusion can be "all" to only include subjects where ALL waves are present or "any" to include subjects 
    where any wave is present.
    """
    beta_paths = glob(
        beta_glob)
    scan_list = ["'" + bp + ",1'" for bp in beta_paths]

    # for sli in scan_list:
    #     print(sli)

    # turn the scan list into a dataframe we can match on.
    subj_beta_list = [re.match(".*sub-(DEV\d*)/", sli)[1] for sli in scan_list]
    beta_df = pd.DataFrame({
        'subject_id': subj_beta_list,
        'spm_l2_path': beta_paths,
        'spm_l2_path_description': scan_list
    })

    # beta_df['spm_l2_path_description'] =beta_df.beta_filepath

    #other data for inclusion
    data_by_ppt = pd.read_csv(dropbox_datapath + "/data_by_ppt.csv")
    data_by_ppt['data_by_ppt_merge_status'] = 'participant_present'
    print("loaded " + str(len(data_by_ppt)) + " rows from data_by_ppt.csv")
    # include_exclude_list = pd.read_csv(ml_scripting_path + "/nsc_subject_exclusions.csv")
    # print("loaded " + str(len(include_exclude_list)) + " rows from nsc_subject_exclusions.csv")
    
    # exclude_subjects = ['DEV061', 'DEV185', 'DEV187', 'DEV189', 'DEV190', 'DEV192', 'DEV198', 'DEV203', 'DEV220',
    #                         'DEV221']
    #also want to exclude subjects whose data was marked questionable in Redcap/Teams

    #scan room data quality
    raise NotImplementedError("need to code this to handle exclusions of individual runs.")
    redcap_data_quality = pd.read_excel(dropbox_datapath + "/DEV-BothSessionsDataQualityC_DATA.xlsx", engine = 'openpyxl')
    #use a regex to extract the wave number from the redcap event name column which comes in the form session_{wave}_arm_\d
    redcap_data_quality['wave'] = redcap_data_quality['redcap_event_name'].str.extract(r'session_(\d)_arm_\d').astype(int)
    
    
    data_quality_task = redcap_data_quality.loc[redcap_data_quality[task].isna()==False,]
    print(str(len(data_quality_task)) + " total sessions from "
          + str(len(data_quality_task['dev_id'].unique())) + " subjects in task Redcap scanner notes, added to the provision useable_dev_id list.")
    redcap_data_quality = data_quality_task.loc[:,['dev_id','wave']][data_quality_task[task]=="No reported problems"]
    # if subj_wave_inclusion=='any':
    #     pass
    # elif subj_wave_inclusion=='all':
    #     usable_sessions2 = redcap_data_quality
    # .groupby('dev_id').filter(lambda x: len(x)==2)

    print(str(len(redcap_data_quality)) + " sessions from "
          + str(len(redcap_data_quality
          ['dev_id'].unique())) + " subjects with no reported problems in task Redcap scanner notes, added to the provision useable_dev_id list.")
    
    #hard-coded excluded subjects
    data_missing_includes = pd.read_csv(dropbox_datapath + "/post-processing-fmri-data-inclusion.csv")

    sst_data_missing_excludes = data_missing_includes['DevID'][data_missing_includes[task]=='Exclude'].tolist()

    print(str(len(sst_data_missing_excludes)) + " subjects excludeable for missing scan data.")
    redcap_data_quality = redcap_data_quality
    [redcap_data_quality
    ['dev_id'].isin(sst_data_missing_excludes)==False]
    print(str(len(redcap_data_quality
    )) + " sessions remaining on the provision useable_dev_id list from the redcap list after excluding subjects with missing scan data.")
    #and exclude subjects excluded by the motion quality process
    #read the CSV, discarding the first line and using the second as headers

    motion_exclusions = pd.read_csv(dropbox_datapath + '/DEVQC_all_subjects - All.csv', header=1)
    #motion_exclusions_w1 = motion_exclusions[motion_exclusions['wave']==1]

    general_motion_exclusion_binvec = motion_exclusions['Exclude'].str.contains('exclude', flags=re.IGNORECASE)
    task_motion_exclusions_binvec = motion_exclusions[task + "_Exclude"].str.contains('exclude', flags=re.IGNORECASE)
    motion_exclusions2 = motion_exclusions.loc[:,['subjectID','wave']][general_motion_exclusion_binvec | task_motion_exclusions_binvec]
    #get thes ubset of redcap_data_quality
    #  where dev_id, wave pairs are not in motion_exclusions2
    #convert motion_exclusions2 into a list of tuples
    motion_exclusions2_tuples = [tuple(x) for x in motion_exclusions2[['subjectID','wave']].to_numpy()]
    usable_sessions_tuples = [tuple(x) for x in redcap_data_quality
    [['dev_id','wave']].to_numpy()]
    usable_sessions2= redcap_data_quality
    [[(r not in motion_exclusions2_tuples) for r in usable_sessions_tuples]]

    #redcap_data_quality
    #  = redcap_data_quality
    # [redcap_data_quality
    # ['subjectID'].isna()]
    print(str(len(redcap_data_quality
    )) + " sessions remaining on the provisional useable_dev_id list from the redcap list after excluding subjects excluded by motion quality process.")

    #raise NotImplementedError("this still ruels out whole sets of ROC and WTP for single runs that are out; we should be more precise than this.")
    #raise NotImplementedError("need to re-write this to handle exclusion for WTP and ROC as well as SST, depnding on task passed in to the function")
    
    print("beta paths before exclusion: " + str(len(beta_df)))
    #included_betas = beta_df[(beta_df.subject_id.isin(exclusion_list_sst.SubjectId)==False)].reset_index(inplace=False, drop=True)
    selected_betas = beta_df.reset_index(inplace=False, drop=True)
    #print("beta paths after exclusion via nsc_subject_exclusions: " + str(len(included_betas)))

    #betas with data is just the paths of all the betas where hter is beta data, i.e., beta files that exist
    betas_with_data = selected_betas.merge(data_by_ppt, left_on='subject_id', right_on='SID')
    #useable dev ids is the list of dev ids that have data and aren't excluded for one reason or another
    #there's two different questions we can ask here:
    #why are there so many subjects where the data is "useable" but there is no beta data and
    #why there so many subjects with beta data but exluded for one reason or another
    #we do actually know why sbjects re exclued, more or less. the question is where all the beta data went.
    if subj_wave_inclusion=='any':
        usable_dev_ids = usable_sessions2['dev_id'].unique().tolist()
    elif subj_wave_inclusion=='all':
        usable_dev_ids = usable_sessions2.groupby('dev_id').filter(lambda x: len(x)==2)['dev_id'].unique().tolist()
    useable_betas_with_data = betas_with_data.loc[betas_with_data.subject_id.isin(usable_dev_ids),]

    #get subjects in usable_dev_ids without an entry in betas_with_data.subject_id
    # only_in_betas = set(betas_with_data.subject_id) - set(usable_dev_ids)
    # only_in_usable_dev_ids = list(set(usable_dev_ids) - set(betas_with_data.subject_id))
    # only_in_usable_dev_ids.sort()



    # print("beta paths after exclusion via nsc_subject_exclusions and the provision useable_dev_id list: " + str(len(useable_betas_with_data)))
        

    useable_betas_with_data.sort_values('subject_id', inplace=True)

    return useable_betas_with_data



def filter_for_selected_data(session_quality_data, scanner_room_report_pass, motion_check_pass, subj_wave_inclusion='all'):

    beta_exists = (
        (session_quality_data.spm_l2_path.isna()==False)
            & (session_quality_data.spm_l2_path != '')
    )
    print("subjects who did or did not have beta data:")
    print(beta_exists.value_counts())


    behavioral_data_exists = (session_quality_data.data_by_ppt_merge_status=='participant_present')
    print("subjects who did or did not have behavioral data:")
    print(behavioral_data_exists.value_counts())
    
    selected_data = (
        session_quality_data[
            #redcap
            scanner_room_report_pass
            #motion exclude
            & motion_check_pass
            #betas
            & beta_exists
            #behavioral
            & behavioral_data_exists
        ]
    )
    return(selected_data)

def get_data_appearing_across_waves(selected_data, subj_wave_inclusion='all'):

    
    #data_by_wave = [selected_data[session_quality_data.wave_id==w] for w in selected_data.wave_id.unique()]
    data_by_wave = [selected_data[selected_data.wave_id==w] for w in selected_data.wave_id.unique()]


    #then only include subjects that are in all waves
    if subj_wave_inclusion=='all':
        set_list = [set(d.subject_id) for d in data_by_wave]
        #get the intersection of the sets in set_list

        subjects_in_all_waves = set.intersection(*set_list)
        data_by_wave = [d[d.subject_id.isin(subjects_in_all_waves)] for d in data_by_wave]
        selected_data_with_all_waves = selected_data[selected_data.subject_id.isin(subjects_in_all_waves)]

    return(selected_data_with_all_waves)


def get_sst_data_for_confirmed_sessions_across_tasks(
        beta_glob,
        dropbox_datapath,
        subj_wave_inclusion = 'all'
    ):
    session_quality_data = get_session_data_quality(beta_glob=beta_glob, dropbox_datapath=dropbox_datapath)

    scanner_room_report_pass = (session_quality_data.redcap_SST=='No reported problems')
    print("subjects who did or did not pass the scanner room report check:")
    print(session_quality_data.groupby('redcap_SST').size())
    print(scanner_room_report_pass.value_counts())


    motion_check_pass = (
        (session_quality_data.motion_exclude_SST_Exclude.isna()==True)
        & (session_quality_data.motion_exclude_SST_Exclude != '')
    )
    print('subjects who did or did not pass the motion check:')
    print(motion_check_pass.value_counts())
    
    #with a set of filters we have just extracted, filter the wave data 
    selected_data = filter_for_selected_data(session_quality_data, scanner_room_report_pass, motion_check_pass, subj_wave_inclusion=subj_wave_inclusion)
    selected_data_with_all_waves = get_data_appearing_across_waves(selected_data, subj_wave_inclusion=subj_wave_inclusion)

    return(selected_data_with_all_waves)

def get_task_data_for_confirmed_sessions(
        beta_glob,
        dropbox_datapath,
        subj_wave_inclusion = 'all',
        task='WTP'
    ):
    session_quality_data = get_session_data_quality(beta_glob=beta_glob, dropbox_datapath=dropbox_datapath)
    
    
    scanner_room_report_pass = (session_quality_data['redcap_' + task + '_quality_any']==1)
    print("subjects who did or did not pass the scanner room report check:")
    print(scanner_room_report_pass.value_counts())


    motion_check_pass = (
        (session_quality_data['motion_exclude_' + task + '_Exclude'].isna()==True)
        & (session_quality_data['motion_exclude_' + task + '_Exclude'] != '')
    )
    print('subjects who did or did not pass the motion check:')
    print(motion_check_pass.value_counts())
    
    #with a set of filters we have just extracted, filter the wave data 
    selected_data = filter_for_selected_data(session_quality_data, scanner_room_report_pass, motion_check_pass, subj_wave_inclusion=subj_wave_inclusion)
    selected_data_with_all_waves = get_data_appearing_across_waves(selected_data, subj_wave_inclusion=subj_wave_inclusion)

    return(selected_data_with_all_waves)

def get_subject_wise_table_with_task_counts(full_table):
    subject_wise_table = get_subject_wise_table(full_table)
    for task in ['ROC','WTP']:
        task_quality_list_col =task + '_quality_list'
        #create a list of the indices of the runs that are not zero
        active_run_list_function = lambda run_binary: [i + 1 for i, x in enumerate(run_binary.tolist()) if x != 0]
        full_table[task_quality_list_col] = full_table.filter(regex='(combined)_' + task + '\d_quality').apply(active_run_list_function,axis=1).tolist()

        #now create a list of the lists, grouping by subID
        quality_list_by_sid = full_table.groupby('SID')[task_quality_list_col].apply(list).apply(lambda x: json.dumps(x)).reset_index(name=task_quality_list_col)
        subject_wise_table = subject_wise_table.merge(quality_list_by_sid, left_on='SID', right_on='SID', how='left')
    
    return (subject_wise_table)

def get_subject_wave_wise_table_with_task_counts(full_table):
    subject_wise_table = get_subject_wise_table(full_table)
    #create a double subject_wise_table, with every row repeated for each of the two waves
    subject_wave_wise_table = pd.concat([subject_wise_table.copy(),subject_wise_table.copy()],axis=0)
    subject_wave_wise_table['wave_id'] = subject_wave_wise_table.groupby('subject_id').cumcount() + 1
    

    for task in ['ROC','WTP']:
        task_quality_list_col =task + '_quality_list'
        #create a list of the indices of the runs that are not zero
        active_run_list_function = lambda run_binary: [i + 1 for i, x in enumerate(run_binary.tolist()) if x != 0]
        full_table[task_quality_list_col] = full_table.filter(regex='(combined)_' + task + '\d_quality').apply(active_run_list_function,axis=1).tolist()

        #now create a list of the lists, grouping by subID
        quality_list_by_sid = full_table[['SID','wave_id',task_quality_list_col]].copy()#.apply(lambda x: json.dumps(x)).reset_index(name=task_quality_list_col)
        quality_list_by_sid[task_quality_list_col] = quality_list_by_sid[task_quality_list_col].apply(lambda x: json.dumps(x))
        subject_wave_wise_table = subject_wave_wise_table.merge(quality_list_by_sid, left_on=['subject_id','wave_id'], right_on=['SID','wave_id'], how='left')
    
    return (subject_wave_wise_table)


def get_subject_wise_table(full_table):
        #identify columns with no values that differ within each SID
    #these are the columns we can drop
    #the count of vlaues has to include NaN as a value
    max_unique_value_count = full_table.groupby('SID').nunique(dropna=False).max()
    subject_wise_cols = ['SID'] + max_unique_value_count[max_unique_value_count==1].index.tolist()
    #cols_to_remove = full_table.columns.difference(subject_wise_cols)
    if 'spm_l2_path' not in subject_wise_cols:
        #print a warning using Warning
        Warning('spm_l2_path not in subject_wise_cols')
        
    #assert ('spm_l2_path' in subject_wise_cols)
    subject_wise_table = full_table.loc[:,subject_wise_cols].drop_duplicates(inplace=False)
    subject_wise_table.reset_index(inplace=True, drop=True)
    return(subject_wise_table)


def get_task_subj_folder_paths_for_subjs_w_two_sessions(
        beta_glob,
        dropbox_datapath,
        task
):
    """
    gets a list of subject folders for subjects with two sessions for the specified task
    all other information is redacted
    A future version might include more information, just cutting out wave-specific data,
    but including subject-specific data.
    """
    full_table = get_task_data_for_confirmed_sessions(
        beta_glob=beta_glob,
        dropbox_datapath=dropbox_datapath,
        subj_wave_inclusion='all',
        task=task
    )

    subject_wise_table = get_subject_wise_table(full_table)


    return(subject_wise_table)


def get_sst_subj_folder_paths_for_subjs_w_two_sessions(
        beta_glob,
        dropbox_datapath
):
    """
    gets a list of subject folders for subjects with two SST sessions
    all other information is redacted
    A future version might include more information, just cutting out wave-specific data,
    but including subject-specific data.
    """
    full_table = get_sst_data_for_confirmed_sessions_across_tasks(
        beta_glob=beta_glob,
        dropbox_datapath=dropbox_datapath,
        subj_wave_inclusion='all'
    )

    subject_wise_table = get_subject_wise_table(full_table)


    return(subject_wise_table)


def get_session_data_quality(
        beta_glob,
        dropbox_datapath,
        task='SST'
        ):
    raise Exception("function get_session_data_quality is deprecated. Use get_session_data_quality_l2 instead, or if you want to get data for level 1, try get_session_data_quality_l1.")

def get_session_data_quality_l2(
        beta_glob,
        dropbox_datapath,
        task='SST'
        ):
    """
    Based on get_data_for_confirmed_train_subjs
    I've taken out the code to exclude subjects based on the train/test split because this is no longer relevant
    However, this now includes code to decide which group of subjects to examine: wave 1, wave 2, or both waves.
    subj_wave_inclusion can be "all" to only include subjects where ALL waves are present or "any" to include subjects 
    where any wave is present.
    """
    beta_paths = glob(
        beta_glob)
    scan_list = ["'" + bp + ",1'" for bp in beta_paths]

    # for sli in scan_list:
    #     print(sli)

    # turn the scan list into a dataframe we can match on.
    subj_beta_list = [re.match(".*sub-(DEV\d*)/", sli)[1] for sli in scan_list]
    beta_df = pd.DataFrame({
        'subject_id': subj_beta_list,
        'spm_l2_path': beta_paths,
        'spm_l2_path_description': scan_list
    })

    #now combine:
    all_data_by_session = get_overall_session_data_quality(
        dropbox_datapath,
        image_folder_df = beta_df
    )
    return(all_data_by_session)


def get_session_data_quality_l1(
        image_folder_glob,
        dropbox_datapath,
        task='SST'
        ):
    """
    Based on get_data_for_confirmed_train_subjs
    I've taken out the code to exclude subjects based on the train/test split because this is no longer relevant
    However, this now includes code to decide which group of subjects to examine: wave 1, wave 2, or both waves.
    subj_wave_inclusion can be "all" to only include subjects where ALL waves are present or "any" to include subjects 
    where any wave is present.
    """
    image_folder_paths = glob(
        image_folder_glob)
    #scan_list = ["'" + bp + ",1'" for bp in image_folder_paths]

    # for sli in scan_list:
    #     print(sli)

    # turn the scan list into a dataframe we can match on.
    subj_image_folder_list = [re.match(".*sub-(DEV\d*)/", sli)[1] for sli in image_folder_paths]
    image_folder_df = pd.DataFrame({
        'subject_id': subj_image_folder_list,
        'spm_l1_path': image_folder_paths#,
        #'spm_l1_path_description': scan_list
    })

    #now combine:
    all_data_by_session = get_overall_session_data_quality(
        dropbox_datapath,
        image_folder_df = image_folder_df
    )
    return(all_data_by_session)



def get_overall_session_data_quality(dropbox_datapath, image_folder_df=None, automotion_datapath=None):
    """
    Gets session data quality but unspecific to the specific task, so, does not check for the presence of beta files.

    """
    if automotion_datapath is None:
        raise Exception("automotion_datapath must be specified")


    #other data for inclusion
    data_by_ppt = pd.read_csv(dropbox_datapath + "/data_by_ppt.csv")
    data_by_ppt['data_by_ppt_merge_status'] = 'participant_present'
    print("loaded " + str(len(data_by_ppt)) + " rows from data_by_ppt.csv")
    # include_exclude_list = pd.read_csv(ml_scripting_path + "/nsc_subject_exclusions.csv")
    # print("loaded " + str(len(include_exclude_list)) + " rows from nsc_subject_exclusions.csv")
    
    # exclude_subjects = ['DEV061', 'DEV185', 'DEV187', 'DEV189', 'DEV190', 'DEV192', 'DEV198', 'DEV203', 'DEV220',
    #                         'DEV221']
    #also want to exclude subjects whose data was marked questionable in Redcap/Teams

    #scan room data quality
    # if task != 'SST':
    #     raise NotImplementedError("need to code this to handle exclusions of individual runs.")
    
    redcap_data_quality = pd.read_excel(dropbox_datapath + "/DEV-BothSessionsSeparateRunsDataQualityC_DATA.xlsx", engine = 'openpyxl')
    #append column names with 'redcap_' to avoid confusion with other data
    redcap_data_quality.columns = ['redcap_' + c for c in redcap_data_quality.columns]
    
    #use a regex to extract the wave number from the redcap event name column which comes in the form session_{wave}_arm_\d
    redcap_data_quality['redcap_wave'] = redcap_data_quality['redcap_redcap_event_name'].str.extract(r'session_(\d)_arm_\d').astype(int)


    labelled_exclusions = pd.read_csv(dropbox_datapath + '/DEVQC_all_subjects - All.csv', header=1)
    #motion_exclusions_w1 = motion_exclusions[motion_exclusions['wave']==1]

    labelled_exclusions.columns = ['labelled_exclusion_' + c for c in labelled_exclusions.columns]

    # motion exclude this is arranged by-participant, not by session
    automotion_exclude = pd.read_csv(automotion_datapath)
    automotion_exclude.columns = ['automotion_exclude_' + c for c in automotion_exclude.columns]

    

    # general_motion_exclusion_binvec = motion_exclusions['Exclude'].str.contains('exclude', flags=re.IGNORECASE)
    # task_motion_exclusions_binvec = motion_exclusions[task + "_Exclude"].str.contains('exclude', flags=re.IGNORECASE)
    # motion_exclusions2 = motion_exclusions.loc[:,['subjectID','wave']][general_motion_exclusion_binvec | task_motion_exclusions_binvec]
    #get thes ubset of redcap_data_quality
    #  where dev_id, wave pairs are not in motion_exclusions2
    #convert motion_exclusions2 into a list of tuples
    # motion_exclusions2_tuples = [tuple(x) for x in motion_exclusions2[['subjectID','wave']].to_numpy()]
    # usable_sessions_tuples = [tuple(x) for x in redcap_data_quality
    # [['dev_id','wave']].to_numpy()]
    # usable_sessions2= redcap_data_quality
    # [[(r not in motion_exclusions2_tuples) for r in usable_sessions_tuples]]


    #redcap_data_quality
    #  = redcap_data_quality
    # [redcap_data_quality
    # ['subjectID'].isna()]
    # print(str(len(redcap_data_quality
    # )) + " sessions remaining on the provisional useable_dev_id list from the redcap list after excluding subjects excluded by motion quality process.")

    #raise NotImplementedError("this still ruels out whole sets of ROC and WTP for single runs that are out; we should be more precise than this.")
    #raise NotImplementedError("need to re-write this to handle exclusion for WTP and ROC as well as SST, depnding on task passed in to the function")

    #data quality cols are: 
    # data_by_ppt:  data_by_ppt_merge_status
    # redcap_data_quality: redcap_SST
    #               redcap_WTP
    #               redcap_ROC
    # data_missing_includes:
    #              manual_exclude_SST
    #              manual_exclude_WTP
    #              manual_exclude_ROC
    # motion_exclusions:
    #               motion_exclusions_Exclude
    #               motion_exclusions_SST_Exclude
    #               motion_exclusions_WTP_Exclude
    #               motion_exclusions_ROC_Exclude
    #data present columns are (cols to check whether a data source includes an entry):
    # beta_df: spm_l2_path
    # data_by_ppt:  data_by_ppt_merge_status
    # redcap_data_quality: columns preceded with 'redcap_{Task}'
    # data_missing_includes: columns preceded with 'manual_exclude_{Task}'
    # motion_exclusions: motion_exclusions_Exclude, motion_exclusions_{Task}_Exclude
    #first merge by-participant data
    if image_folder_df is not None:
        image_folder_df.rename(columns={'subject_id':'beta_subject_id'}, inplace=True)
        data_by_ppt_all = image_folder_df.merge(data_by_ppt, left_on='beta_subject_id', right_on='SID', how='outer')
        print(image_folder_df.shape, data_by_ppt.shape, data_by_ppt_all.shape)
        #make sure there's a column that stores IDs across the merged columns
        data_by_ppt_all['subject_id'] = [r['beta_subject_id'] if not pd.isna(r['beta_subject_id']) else r['SID'] for i, r in data_by_ppt_all.iterrows()]
    else: #no session data; create a table that stores everything except beta data about useable sessions.
        data_by_ppt_all = data_by_ppt
        data_by_ppt_all['subject_id'] = data_by_ppt_all['SID']
    #now merge by-session data
    data_by_session_merge1=redcap_data_quality.merge(labelled_exclusions, left_on=['redcap_dev_id','redcap_wave'], right_on=['labelled_exclusion_subjectID','labelled_exclusion_wave'], how='outer')
    #make sure there's a column that stores IDs across the merged columns
    data_by_session_merge1['subject_id'] = [r['redcap_dev_id'] if not pd.isna(r['redcap_dev_id']) else r['labelled_exclusion_subjectID'] for i, r in data_by_session_merge1.iterrows()]
    data_by_session_merge1['wave_id'] = [r['redcap_wave'] if not pd.isna(r['redcap_wave']) else r['labelled_exclusion_wave'] for i, r in data_by_session_merge1.iterrows()]
    print(redcap_data_quality.shape, labelled_exclusions.shape, data_by_session_merge1.shape)
    #now merge in teh by-session data with the by-ppt data
    data_by_session_merge2 = data_by_ppt_all.merge(data_by_session_merge1, left_on=['subject_id'], right_on=['subject_id'], how='outer')
    print(data_by_ppt_all.shape, data_by_session_merge1.shape, data_by_session_merge2.shape)

    # now merge in the by-session data with automotion_exclude data
    data_by_session_merge3 = data_by_session_merge2.merge(automotion_exclude, left_on=['subject_id','wave_id'], right_on=['automotion_exclude_subjectID','automotion_exclude_wave'], how='outer')

    

    all_data_by_session = data_by_session_merge3

    all_data_by_session.sort_values(['subject_id','wave_id'], inplace=True)
    all_data_by_session.reset_index(inplace=True, drop=True)

    #now place the indicator columns at the beginning of the dataframe, using a regex match on the columns
    indicator_cols = [c for c in all_data_by_session.columns if re.match(r'.*(subject_id|wave|SID|dev_id).*', c)]
    print(indicator_cols)

    #now re-arrange so that the indicator columns are first
    # and then all the exclusion columns follow
    redcap_sst_cols = ['redcap_SST']
    redcap_wtp_cols = ['redcap_WTP' + str(i) for i in range(1,5)]
    redcap_roc_cols = ['redcap_ROC' + str(i) for i in range(1,5)]

    labelled_sst_cols = ['labelled_exclusion_SST_Exclude']
    labelled_wtp_cols = ['labelled_exclusion_WTP' + str(i) + '_Exclude' for i in range(1,5)]
    labelled_roc_cols = ['labelled_exclusion_ROC' + str(i) + '_Exclude' for i in range(1,5)]

    motion_sst_cols = ['automotion_exclude_SST1']
    motion_wtp_cols = ['automotion_exclude_WTP' + str(i) + '' for i in range(1,5)]
    motion_roc_cols = ['automotion_exclude_ROC' + str(i) + '' for i in range(1,5)]

    
    exclusion_columns =  (['data_by_ppt_merge_status'] + redcap_sst_cols + 
                          redcap_wtp_cols + 
                          redcap_roc_cols + 
                          #[c for c in all_data_by_session.columns if re.match(r'motion_exclude.*(Exclude).*', c)]
                            labelled_sst_cols +
                            labelled_wtp_cols +
                            labelled_roc_cols + 
                            motion_sst_cols +
                            motion_wtp_cols +
                            motion_roc_cols
    )

    other_cols = [c for c in all_data_by_session.columns if c not in indicator_cols + exclusion_columns]

    all_data_by_session = all_data_by_session[indicator_cols + exclusion_columns + other_cols]

    #quantifying columns indicating quality from the redcap (scan room data) for each ROC and WTP session
    for task, task_cols in {
        'ROC': redcap_roc_cols, 
        'WTP': redcap_wtp_cols, 
        'SST': redcap_sst_cols
    }.items():
        for col in task_cols:
            all_data_by_session.loc[:,col + '_quality'] = all_data_by_session[col].apply(lambda x: 1 if x=='No reported problems' else 0)

        task_cols_quality = [col + '_quality' for col in task_cols]
        #now quantify the overall quality, indicating whether, 
        # across all cols in task_cols, at least one column has quality
        all_data_by_session['redcap_' + task + '_quality_any'] = all_data_by_session[task_cols_quality].apply(lambda x: 1 if x.sum()>0 else 0, axis=1)

    #now do the same for labelled exclusions
    for task, task_cols in {
        'ROC': labelled_roc_cols, 
        'WTP': labelled_wtp_cols, 
        'SST': labelled_sst_cols
    }.items():
        for col in task_cols:
            all_data_by_session[col + '_quality'] = all_data_by_session[col].apply(lambda x: 1 if pd.isna(x) or x=="" else 0)

        task_cols_quality = [col + '_quality' for col in task_cols]
        #now quantify the overall quality, indicating whether, 
        # across all cols in task_cols, at least one column has quality
        all_data_by_session['labelled_' + task + '_quality_any'] = all_data_by_session[task_cols_quality].apply(lambda x: 1 if x.sum()>0 else 0, axis=1)

    #now do the same for motion
    for task, task_cols in {
            'SST': motion_sst_cols,
            'WTP': motion_wtp_cols,
            'ROC': motion_roc_cols
        }.items():
        for col in task_cols:
            all_data_by_session[col + '_quality'] = all_data_by_session[col].apply(lambda x: 0 if pd.isnull(x) or x>10 else 1)

        task_cols_quality = [col + '_quality' for col in task_cols]
        #now quantify the overall quality, indicating whether, 
        # across all cols in task_cols, at least one column has quality
        all_data_by_session['automotion_' + task + '_quality_any'] = all_data_by_session[task_cols_quality].apply(lambda x: 1 if x.sum()>0 else 0, axis=1)


    #find columns with 'redcap' in the name
    [c for c in all_data_by_session.columns if re.match(r'.*(redcap).*', c)]

    #now combine across the three quality indicators
    task_run_counts = {
        'ROC': 4,
        'WTP': 4,
        'SST': 1
    }
    for task, task_run_count in task_run_counts.items():
        if task=='SST':
            all_data_by_session['combined_' + task + '_quality'] = (
                all_data_by_session[[
                    'redcap_' + task + '_quality', 
                    'labelled_exclusion_' + task + '_Exclude_quality',  #changed from 'Exclude_quality'; why is this?
                    'automotion_exclude_' + task + '1_quality']].apply(lambda x: 1 if x.sum()==3 else 0, axis=1)
            )
        else:
            for run_i in range(1, task_run_count+1):
                all_data_by_session['combined_' + task + str(run_i) + '_quality' + str(run_i)] = (
                    all_data_by_session[[
                        'redcap_' + task + str(run_i) + '_quality', 
                        'labelled_exclusion_' + task + str(run_i) + '_Exclude_quality',
                        'automotion_exclude_' + task + str(run_i) + '_quality'
                        ]].apply(lambda x: 1 if x.sum()==3 else 0, axis=1)
                )


    return all_data_by_session