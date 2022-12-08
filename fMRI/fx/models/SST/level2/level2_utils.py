import datetime
import pandas as pd
import numpy as np
import os
from glob import glob
import re
import scipy.io
import yaml
import socket
#import regex package
import re

def read_yaml_for_host(file_path):
    hostname = socket.gethostname()
    with open(file_path, "r") as f:
        return yaml.safe_load(f)[hostname]

def get_contrasts_for_betas(
        betas
):
    betas['spm_l2_targeted_contrast_filepath'] = None

    betas.reset_index(inplace=True,drop=True)


    for beta_i, beta_folderpath in enumerate(betas.spm_l2_path):
        print(beta_folderpath)
        # load the mat file associated with the current run
        subj_l1_mat_config = scipy.io.loadmat(str(
            beta_folderpath + '/SPM.mat'), appendmat=False, simplify_cells=True, variable_names='SPM')

        # get the list of level 1 contrasts that are included in the level 1 analysis we're examining
        # contrasts_in_run = [contrast['name'] for contrast in subj_l1_mat_config['SPM']['xCon']]

        # which is it?
        # contrast_index = [c_i for c_i, contrast in enumerate(subj_l1_mat_config['SPM']['xCon'])
        #                   if contrast['name'] == contrast_to_extract
        #                   ][0]

        for c_i, contrast in enumerate(subj_l1_mat_config['SPM']['xCon']):
            print(str(c_i) + ": " + contrast['name'] + " " + contrast['Vspm']['fname'])
            betas.loc[beta_i, 'contrast_' + contrast['name'] + "_fname"] =contrast['Vspm']['fname']

        # if contrast_index is None:
        #     print("this run does not contain the targeted contrast.")
        # else:
        #     return (contrast_index)

        #betas.loc[beta_i, 'spm_l2_targeted_contrast_filepath'] =
    # test if the contrast we want is there

    return (betas)


#here we're going to find a way to pass betas themselves instead of contrasts
def get_beta_fnames_for_beta_dirs(
        beta_dir_df
):
    beta_dir_df['spm_l2_targeted_contrast_filepath'] = None

    beta_dir_df.reset_index(inplace=True,drop=True)

    for beta_i, beta_folderpath in enumerate(beta_dir_df.spm_l2_path):
        print(beta_folderpath)
        # load the mat file associated with the current run
        subj_l1_mat_config = scipy.io.loadmat(str(
            beta_folderpath + '/SPM.mat'), appendmat=False, simplify_cells=True, variable_names='SPM')

        # get the list of level 1 contrasts that are included in the level 1 analysis we're examining
        # contrasts_in_run = [contrast['name'] for contrast in subj_l1_mat_config['SPM']['xCon']]

        # which is it?
        # contrast_index = [c_i for c_i, contrast in enumerate(subj_l1_mat_config['SPM']['xCon'])
        #                   if contrast['name'] == contrast_to_extract
        #                   ][0]

        for b_i, vbeta in enumerate(subj_l1_mat_config['SPM']['Vbeta']):
            beta_readable_description = re.search(r'Sn\(1\) (.*?)(\^\d)?(\*bf\(1\))?$', vbeta['descrip'])[1]
            #print(str(b_i) + ": " + beta_readable_description + " " + vbeta['fname'])
            beta_dir_df.loc[beta_i, 'beta_' + beta_readable_description + "_fname"] =vbeta['fname']

        # if contrast_index is None:
        #     print("this run does not contain the targeted contrast.")
        # else:
        #     return (contrast_index)

        #betas.loc[beta_i, 'spm_l2_targeted_contrast_filepath'] =
    # test if the contrast we want is there

    return (beta_dir_df)



def get_data_for_confirmed_train_subjs(
        beta_glob,
        nonbids_data_path,
        dropbox_datapath,
        ml_scripting_path,
        exclude_test_subjs=True
        ):
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
    include_exclude_list = pd.read_csv(ml_scripting_path + "/nsc_subject_exclusions.csv")
    #hard-coded excluded subjects
    exclude_subjects = ['DEV061', 'DEV185', 'DEV187', 'DEV189', 'DEV190', 'DEV192', 'DEV198', 'DEV203', 'DEV220',
                            'DEV221']
    #also want to exclude subjects whose data was marked questionable in Redcap/Teams
    data_quality = pd.read_excel(dropbox_datapath + "/DEV-Session1DataQualityC_DATA.xlsx", engine = 'openpyxl')
    data_quality_sst = data_quality.loc[data_quality.SST.isna()==False,]
    usable_dev_ids = data_quality_sst.dev_id[data_quality_sst.SST=="No reported problems"]

    if exclude_test_subjs:
        # get just the training subjects
        test_train_df_raw = pd.read_csv(nonbids_data_path + "fMRI/ml/train_test_markers_20220818T144138.csv")
        test_train_df_raw = test_train_df_raw.merge(include_exclude_list[include_exclude_list.Task == 'SST'],
                                                    left_on='sub_label', right_on='SubjectId', how='left')
        test_train_df_raw.loc[test_train_df_raw.Include.isna(), 'Include'] = True
        test_train_df = test_train_df_raw[test_train_df_raw.Include == True]
        train_subjs = test_train_df.loc[
            test_train_df.SplitGroup_75_25 == 'Train', 'sub_label'].tolist()  # only get the train subjects; ignore those previously marked hold-out

        # now merge the train list with the beta list, the data list, and the useable subject list
        train_betas = beta_df[(beta_df.subject_id.isin(train_subjs))].reset_index(inplace=False, drop=True)
        train_betas_with_data = train_betas.merge(data_by_ppt, left_on='subject_id', right_on='SID')
        useable_train_betas_with_data = train_betas_with_data.loc[train_betas_with_data.subject_id.isin(usable_dev_ids),]
    else:
        include_exclude_list.loc[include_exclude_list.Include.isna(), 'Include'] = True
        exclusion_list_sst = include_exclude_list[(include_exclude_list.Task == 'SST') & include_exclude_list.Include==False]
        
        included_betas = beta_df[(beta_df.subject_id.isin(exclusion_list_sst.SubjectId)==False)].reset_index(inplace=False, drop=True)
        useable_train_betas_with_data = included_betas.loc[included_betas.subject_id.isin(usable_dev_ids),]
        

    useable_train_betas_with_data.sort_values('subject_id', inplace=True)

    return useable_train_betas_with_data


def create_spm_l2_script(template_filepath, replacement_map, output_filepath):
    ### this function takes a template file and replaces the values in the replacement map
    ### it then outputs the new file to the specified output path
    with open(template_filepath, 'r') as template_file:
        template_string = template_file.read()
    
    for key, value in replacement_map.items():
        template_string = template_string.replace(key, value)

    #get output directory
    output_dir = os.path.dirname(output_filepath)
    #create the dir if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        print("output directory " + output_dir + "already exists")
        
        raise Exception("output directory already exists. Please delete it and try again.")

    with open(output_filepath, 'w') as output_file:
        output_file.write(template_string)
    
    return(output_filepath)

def execute_spm_l2_script(script_to_execute, spm_path):
    ### this function executes the spm l2 script

    # run the script
    os.system('export SCRIPT="' + script_to_execute + '"; echo $SCRIPT; bash simple_spm_job.sh');


def iterate_over_l1_images_and_run_l2_scripts(
    l1_image_name_list, l1_images_with_paths, analysis_name, sst_level_2_path, template_filepath, spm_path,
    col_function = lambda img_name: 'contrast_' + img_name + '_fname'
     ):
    # pull date in format YYYYMMDD
    date_label = datetime.datetime.now().strftime("%Y%m%d")

    for l1_image_name in l1_image_name_list:
        colname = col_function(l1_image_name)
        print(l1_image_name)
        if colname in l1_images_with_paths.columns:
            img_filepath_list = ""
            for i, r in l1_images_with_paths.iterrows():
                if pd.isnull(r[colname]) is False:
                    tmap_filepath = r.loc['spm_l2_path'] + r.loc[colname]
                    tmap_spm_command = "'" + tmap_filepath + ",1'"
                    print(tmap_spm_command)
                    img_filepath_list += tmap_spm_command + "\n"
            output_folderpath=sst_level_2_path + analysis_name + "_" + date_label + "/" + l1_image_name
            output_filepath =output_folderpath + "/" + l1_image_name + "_one_sample_design_estimate.m"
            create_spm_l2_script(template_filepath, replacement_map = {
                    'OUTDIR': output_folderpath,
                    'img_filepath_list': img_filepath_list,
                    '(MAIN HEADER)': l1_image_name
                    },
                output_filepath = output_filepath
                )
            #now run the script
            #now to texecute, something like
            execute_spm_l2_script(output_filepath, spm_path=spm_path)
        else:
            print('contrast ' + l1_image_name + ' not found.')
