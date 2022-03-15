import pandas as pd
import os
from glob import glob
import re


def get_data_for_confirmed_train_subjs(
        beta_glob,
        nonbids_data_path,
        ml_data_folderpath,
        ml_scripting_path):
    beta_paths = glob(
        beta_glob)
    scan_list = ["'" + bp +",1'" for bp in beta_paths]

    # for sli in scan_list:
    #     print(sli)


    #turn the scan list into a dataframe we can match on.
    subj_beta_list = [re.match(".*sub-(DEV\d*)/",sli)[1] for sli in scan_list]
    beta_df = pd.DataFrame({
        'subject_id': subj_beta_list,
        'spm_l2_path': beta_paths,
        'spm_l2_path_description':scan_list
    })

    #beta_df['spm_l2_path_description'] =beta_df.beta_filepath


    #get just the test subjects
    test_train_df_raw = pd.read_csv(nonbids_data_path + "fMRI/ml/train_test_markers_20211027T173724.csv")
    data_by_ppt = pd.read_csv(ml_data_folderpath + "/data_by_ppt_2022_02_26.csv")
    include_exclude_list = pd.read_csv(ml_scripting_path + "/nsc_subject_exclusions.csv")
    test_train_df_raw = test_train_df_raw.merge(include_exclude_list[include_exclude_list.Task=='SST'],left_on='sub_label',right_on='SubjectId',how='left')
    test_train_df_raw.loc[test_train_df_raw.Include.isna(),'Include'] = True
    test_train_df = test_train_df_raw[test_train_df_raw.Include==True]

    exclude_subjects = ['DEV061','DEV185','DEV187','DEV189','DEV190','DEV192','DEV198','DEV203','DEV220','DEV221']
    train_subjs = test_train_df.loc[test_train_df.SplitGroup=='Train','sub_label'].tolist()#only get the train subjects; ignore those previously marked hold-out

    #now merge the train list with the beta list and the data list
    train_betas = beta_df[(beta_df.subject_id.isin(train_subjs))].reset_index(inplace=False,drop=True)
    train_betas_with_data = train_betas.merge(data_by_ppt,left_on='subject_id',right_on='SID')

    train_betas_with_data.sort_values('subject_id', inplace=True)

    return train_betas_with_data





