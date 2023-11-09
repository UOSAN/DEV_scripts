import datetime
import warnings
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
from collections import OrderedDict

def read_yaml_for_host(file_path):
    hostname = socket.gethostname()
    print(hostname)
    with open(file_path, "r") as f:
        yaml_all = yaml.safe_load(f)
        if hostname in yaml_all:
            return yaml_all[hostname]
        else:
            print("hostname '" + hostname + "' not found in yaml file. using default.")
            return yaml.safe_load(f)['default']

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
            beta_match = re.search(r'Sn\((\d+)\) (.*?)(\^\d)?(\*bf\(1\))?$', vbeta['descrip'])
            beta_session_id = int(beta_match[1])
            if beta_session_id!=1:
                raise NotImplementedError("this function only works for single-session data at the moment.")

            beta_readable_description = beta_match[2]
            #print(str(b_i) + ": " + beta_readable_description + " " + vbeta['fname'])
            beta_dir_df.loc[beta_i, 'beta_' + beta_readable_description + "_fname"] =vbeta['fname']

        # if contrast_index is None:
        #     print("this run does not contain the targeted contrast.")
        # else:
        #     return (contrast_index)

        #betas.loc[beta_i, 'spm_l2_targeted_contrast_filepath'] =
    # test if the contrast we want is there

    return (beta_dir_df)


#here we're going to find a way to pass betas themselves instead of contrasts
def get_beta_fname_list_for_beta_dirs(
        beta_dir_df
):
    beta_dir_df['spm_l2_targeted_contrast_filepath'] = None

    beta_dir_df.reset_index(inplace=True,drop=True)

    beta_roi_list = []

    for beta_i, beta_folderpath in enumerate(beta_dir_df.spm_l2_path):
        print(beta_folderpath)
        # load the mat file associated with the current run
        #try to load the file; if it doesn't load, through a warning and move on
        try:
            subj_l1_mat_config = scipy.io.loadmat(str(
            beta_folderpath + '/SPM.mat'), appendmat=False, simplify_cells=True, variable_names='SPM')
        except FileNotFoundError:
            print("could not find SPM.mat in " + beta_folderpath + '/SPM.mat')
            continue


        # get the list of level 1 contrasts that are included in the level 1 analysis we're examining
        # contrasts_in_run = [contrast['name'] for contrast in subj_l1_mat_config['SPM']['xCon']]

        # which is it?
        # contrast_index = [c_i for c_i, contrast in enumerate(subj_l1_mat_config['SPM']['xCon'])
        #                   if contrast['name'] == contrast_to_extract
        #                   ][0]

        for b_i, vbeta in enumerate(subj_l1_mat_config['SPM']['Vbeta']):
            beta_readable_description_wrapped = re.search(r'Sn\((\d)\) (.*?)(\^\d)?(\*bf\(1\))?$', vbeta['descrip'])
            if beta_readable_description_wrapped is None:
                raise Exception("could not find beta description in " + vbeta['descrip'])
                
            beta_run = int(beta_readable_description_wrapped[1])
            beta_readable_description = beta_readable_description_wrapped[2]
            #print(str(b_i) + ": " + beta_readable_description + " " + vbeta['fname'])
            # if beta_dir_df.loc[beta_i, 'beta_' + beta_readable_description + "_fname"] is None:
            #     beta_dir_df.loc[beta_i, 'beta_' + beta_readable_description + "_fname"] =vbeta['fname']
            # else:
            #     beta_dir_df.loc[beta_i, 'beta_' + beta_readable_description + "_fname"] = (
            #         beta_dir_df.loc[beta_i, 'beta_' + beta_readable_description + "_fname"] + "," + vbeta['fname']
            #     )

            beta_roi_list.append({
                'subject_id': beta_dir_df.loc[beta_i, 'subject_id'],
                'spm_l2_path': beta_dir_df.loc[beta_i, 'spm_l2_path'],
                'spm_l2_path_description': beta_dir_df.loc[beta_i, 'spm_l2_path_description'],
                'wave': beta_dir_df.loc[beta_i, 'wave'],
                'spm_l2_targeted_contrast_filepath': beta_dir_df.loc[beta_i, 'spm_l2_targeted_contrast_filepath'],
                'task_run':beta_run,
                'beta_description': beta_readable_description,
                'beta_fname': vbeta['fname']
                
                
            })
                #we'll transform this once we're done, I guess
        
    #turn the ROI list into a single dataframe
    beta_roi_df = pd.DataFrame(beta_roi_list)

    return (beta_roi_df)


def get_data_for_confirmed_train_subjs(
        beta_glob,
        nonbids_data_path,
        dropbox_datapath,
        ml_scripting_path,
        exclude_test_subjs=True,
        task='SST'
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

    print("loaded " + str(len(data_by_ppt)) + " rows from data_by_ppt.csv")
    # include_exclude_list = pd.read_csv(ml_scripting_path + "/nsc_subject_exclusions.csv")
    # print("loaded " + str(len(include_exclude_list)) + " rows from nsc_subject_exclusions.csv")
    
    # exclude_subjects = ['DEV061', 'DEV185', 'DEV187', 'DEV189', 'DEV190', 'DEV192', 'DEV198', 'DEV203', 'DEV220',
    #                         'DEV221']
    #also want to exclude subjects whose data was marked questionable in Redcap/Teams
    #1. this needs to call on session 1, 2, or joint, depending on what we're doing
    #raise NotImplementedError("need to code this to handle exclusions of individual runs.")
    warnings.warn("this uses the obsolete session1 data quality. only really useful for processing single-session data")
    redcap_data_quality = pd.read_excel(dropbox_datapath + "/DEV-Session1DataQualityC_DATA.xlsx", engine = 'openpyxl')
    #redcap_data_quality = pd.read_excel(dropbox_datapath + "/DEV-Session1DataQualityC_DATA.xlsx", engine = 'openpyxl')
    
    data_quality_task = redcap_data_quality.loc[redcap_data_quality[task].isna()==False,]
    usable_dev_ids = data_quality_task.dev_id[data_quality_task[task]=="No reported problems"]
    print(str(len(usable_dev_ids)) + " subjects with no reported problems in task Redcap scanner notes, added to the provision useable_dev_id list.")
    
    #hard-coded excluded subjects
    data_missing_includes = pd.read_csv(dropbox_datapath + "/post-processing-fmri-data-inclusion.csv")

    sst_data_missing_excludes = data_missing_includes['DevID'][data_missing_includes[task]=='Exclude'].tolist()

    print(str(len(sst_data_missing_excludes)) + " subjects excludeable for missing scan data.")
    usable_dev_ids = [id for id in usable_dev_ids if id not in sst_data_missing_excludes]
    print(str(len(usable_dev_ids)) + " subjects remaining on the provision useable_dev_id list from the redcap list after excluding subjects with missing scan data.")
    #and exclude subjects excluded by the motion quality process
    #read the CSV, discarding the first line and using the second as headers
# this also neds to be session 1, 2, or joint
    motion_exclusions = pd.read_csv(dropbox_datapath + '/DEVQC_all_subjects - All.csv', header=1)
    motion_exclusions_w1 = motion_exclusions[motion_exclusions['wave']==1]

    general_motion_exclusion_binvec = motion_exclusions_w1['Exclude'].str.contains('exclude', flags=re.IGNORECASE)
    task_motion_exclusions_binvec = motion_exclusions_w1[task + "_Exclude"].str.contains('exclude', flags=re.IGNORECASE)
    motion_exclusions = motion_exclusions_w1['subjectID'][general_motion_exclusion_binvec | task_motion_exclusions_binvec]

    usable_dev_ids = [id for id in usable_dev_ids if id not in motion_exclusions.tolist()]
    print(str(len(usable_dev_ids)) + " subjects remaining on the provisional useable_dev_id list from the redcap list after excluding subjects excluded by motion quality process.")

    #raise NotImplementedError("this still ruels out whole sets of ROC and WTP for single runs that are out; we should be more precise than this.")
    #raise NotImplementedError("need to re-write this to handle exclusion for WTP and ROC as well as SST, depnding on task passed in to the function")
    
    if exclude_test_subjs:
        # get just the training subjects
        test_train_df_raw = pd.read_csv(nonbids_data_path + "fMRI/ml/train_test_markers_20230102T164214.csv")
        # test_train_df_raw = test_train_df_raw.merge(include_exclude_list[include_exclude_list.Task == task],
        #                                             left_on='sub_label', right_on='SubjectId', how='left')
        test_train_df_raw.loc[test_train_df_raw.Include.isna(), 'Include'] = True
        test_train_df = test_train_df_raw[test_train_df_raw.Include == True]
        train_subjs = test_train_df.loc[
            test_train_df.SplitGroup_75_25 == 'Train', 'sub_label'].tolist()  # only get the train subjects; ignore those previously marked hold-out

        # now merge the train list with the beta list, the data list, and the useable subject list
        selected_betas = beta_df[(beta_df.subject_id.isin(train_subjs))].reset_index(inplace=False, drop=True)
    else:
        # include_exclude_list.loc[include_exclude_list.Include.isna(), 'Include'] = True
        # exclusion_list_sst = include_exclude_list[(include_exclude_list.Task == 'SST') & include_exclude_list.Include==False]
        # print("" + str(len(exclusion_list_sst)) + " subject excludeable from the SST task via nsc_subject_exclusions.csv")
        
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
    useable_betas_with_data = betas_with_data.loc[betas_with_data.subject_id.isin(usable_dev_ids),]

    #get subjects in usable_dev_ids without an entry in betas_with_data.subject_id
    only_in_betas = set(betas_with_data.subject_id) - set(usable_dev_ids)
    only_in_usable_dev_ids = list(set(usable_dev_ids) - set(betas_with_data.subject_id))
    only_in_usable_dev_ids.sort()



    print("beta paths after exclusion via nsc_subject_exclusions and the provision useable_dev_id list: " + str(len(useable_betas_with_data)))
        

    useable_betas_with_data.sort_values('subject_id', inplace=True)

    return useable_betas_with_data



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

def generate_single_confounder_script_fragment(confounder_template_path, confounder_name,confound_i,confounder_contents):
    ### this function takes a template file and replaces the values in the replacement map
    ### it then outputs the new file to the specified output path
    with open(confounder_template_path, 'r') as template_file:
        template_string = template_file.read()
    
    template_string = template_string.replace("CONFOUND_LABEL", confounder_name)
    if confounder_contents is not None:
        confounder_contents_string = "\n".join([str(int(f)) for f in confounder_contents])
        template_string = template_string.replace("CONFOUND_LIST", confounder_contents_string)
        template_string = template_string.replace("weight_vec", confounder_contents_string)
    template_string = template_string.replace("confound_i", str(confound_i))
    #template_string = template_string.replace("weight_vec", " ".join(["0"]*(confound_i-1)) + " 1")
    
    

    return(template_string)

# def generate_confounder_set_script_fragment_from_dataframe(colnames_to_add,subjects_df,confounder_template_path):
#     ### this function takes a template file and replaces the values in the replacement map
#     ### it then returns that for insertion into the main script
#     script_fragment = ""
#     for i, colname in enumerate(colnames_to_add):
#         confound_i = str(i+1)
#         confounder_name = colname
#         confounder_contents = subjects_df[colname].tolist()
#         confounder_script_fragment = generate_single_confounder_script_fragment(confounder_template_path, confounder_name,confound_i,confounder_contents)
#         script_fragment = script_fragment + confounder_script_fragment

#     return(script_fragment)

def generate_contrast_set_script_fragment_from_dict(confounder_dict, confounder_template_path):
    ### this function takes a template file and replaces the values in the replacement map
    ### it then returns that for insertion into the main script
    script_fragment = ""
    for i, (confounder_name, confounder_contents) in enumerate(confounder_dict.items()):
        confound_i = i+1
        confounder_script_fragment = generate_single_confounder_script_fragment(confounder_template_path, confounder_name,confound_i,confounder_contents)
        script_fragment = script_fragment + confounder_script_fragment

    return(script_fragment)

def setup_l2_dir(sst_level_2_path,analysis_name,l1_images_with_paths):
    # pull date in format YYYYMMDD
    date_label = datetime.datetime.now().strftime("%Y%m%d")
    
    output_basedir = sst_level_2_path + analysis_name + "_" + date_label
    #create the dir if it doesn't exist
    if not os.path.exists(output_basedir):
        os.makedirs(output_basedir)

    l1_images_with_paths.to_csv(output_basedir + "/raw_filelist.csv")
    return(output_basedir)

def iterate_over_l1_images_and_run_l2_scripts_w_confounds(
    l1_image_name_list, l1_images_with_paths, analysis_name, sst_level_2_path, template_filepath, spm_path,
    col_function = lambda img_name: 'contrast_' + img_name + '_fname',
    confounders = [], confounder_template_path = None, consess_template_path = None, conspec_template_path = None,
    execute_l2_script = True, include_base_contrast = True, confounder_contrasts = []
     ):
    
    output_basedir = setup_l2_dir(sst_level_2_path,analysis_name,l1_images_with_paths)

    #loop through the l1 images
    for l1_image_name in l1_image_name_list:
        colname = col_function(l1_image_name)
        print(l1_image_name)
        if colname in l1_images_with_paths.columns:
            img_filepath_list = ""

            output_folderpath=output_basedir + "/" + l1_image_name
            output_filepath =output_folderpath + "/" + l1_image_name + "_confounds_design_estimate.m"


            #create a dictionary of empty lists where there's one entry for each string in the list confounders
            #ensure each list is a new copy of the list, not a reference to the same list
            confounder_dict = OrderedDict({k: [] for k in confounders})

            img_filepath_list = populate_filepath_list(l1_images_with_paths,colname)

            for i, r in l1_images_with_paths.iterrows():
                if pd.isnull(r[colname]) is False:
                    #now add the confounders
                    for cf in confounders:
                        confounder_dict[cf].append(r.loc[cf])

            #now we want to go through that confounder dict, and change any null entries to the mean of the column.
            for cf in confounders:
                confounder_dict[cf] = [np.nanmean(confounder_dict[cf]) if np.isnan(x) else x for x in confounder_dict[cf]]

            #now create the contrasts
            contrast_names = list(confounder_dict.keys())
            if include_base_contrast:
                contrast_names = [l1_image_name] + contrast_names

            contrast_dict = OrderedDict((c_k, [0]*c_i + [1] + [0]*(len(contrast_names)-c_i-1)) for c_i,c_k in enumerate(contrast_names))


            if len(confounder_contrasts)>0:
                #these are named contrasts that we want to add to the consess and conspec
                #we'll need to use regex to detect exactly which contrast we're talking about
                #right now we just support '>' contrasts
                for cc in confounder_contrasts:
                    #regex to find the contrast name, assuming there's a > in the middle
                    try:
                        r1, op, r2 = re.search(r'(.*)(\W+)(.*)',cc).groups()
                    except AttributeError:
                        raise Exception("could not parse confounder contrast '" + cc + "'; it may not be in a supported format.")
                    if op=='>':
                        
                        cc_contrast = [r1_i - r2_i for r1_i, r2_i in zip(contrast_dict[r1], contrast_dict[r2])] 

                    else:
                        raise NotImplementedError("we only support > contrasts at the moment.")
                    
                    #all_contrast_dict = OrderedDict((**all_contrast_dict,**OrderedDict({cc:cc_contrast})))
                    contrast_dict.update({cc:cc_contrast})
                    

            #now generate the confounder script fragment
            confounder_script_text = generate_contrast_set_script_fragment_from_dict(confounder_dict, confounder_template_path)
            #for the conspecs and consess we need to pass in the confounder dict AND the main contrast
            contrast_consess_script_text = generate_contrast_set_script_fragment_from_dict(contrast_dict, consess_template_path)

            result_contrast_dict = OrderedDict((l1_image_name + '_' + key, value) for key, value in contrast_dict.items())
            contrast_conspec_script_text = generate_contrast_set_script_fragment_from_dict(result_contrast_dict, conspec_template_path)
            
            create_spm_l2_script(template_filepath, replacement_map = {
                    'OUTDIR': output_folderpath,
                    'img_filepath_list': img_filepath_list,
                    '(MAIN HEADER)': l1_image_name,
                    'CONFOUNDS': confounder_script_text,
                    'CONSESS': contrast_consess_script_text,
                    'CONSPEC': contrast_conspec_script_text
                    },
                output_filepath = output_filepath
                )
            #now run the script
            #now to texecute, something like
            if execute_l2_script:
                execute_spm_l2_script(output_filepath, spm_path=spm_path)
        else:
            print('contrast ' + l1_image_name + ' not found.')


def populate_filepath_list(l1_images_with_paths,colname):
    img_filepath_list = ""
    for i, r in l1_images_with_paths.iterrows():
        if pd.isnull(r[colname]) is False:
            tmap_filepath = r.loc['spm_l2_path'] + r.loc[colname]
            tmap_spm_command = "'" + tmap_filepath + ",1'"
            print(tmap_spm_command)
            img_filepath_list += tmap_spm_command + "\n"

    return(img_filepath_list)

def iterate_over_l1_images_and_run_l2_scripts(
    l1_image_name_list, l1_images_with_paths, analysis_name, sst_level_2_path, template_filepath, spm_path,
    col_function = lambda img_name: 'contrast_' + img_name + '_fname',
    confounders = [], confounder_template_path = None, consess_template_path = None, conspec_template_path = None,
    execute_l2_script = True
     ):
    
    output_basedir = setup_l2_dir(sst_level_2_path,analysis_name,l1_images_with_paths)

    #loop through the l1 images
    for l1_image_name in l1_image_name_list:
        colname = col_function(l1_image_name)
        print(l1_image_name)
        if colname in l1_images_with_paths.columns:
            

            output_folderpath=output_basedir + "/" + l1_image_name
            output_filepath =output_folderpath + "/" + l1_image_name + "_one_sample_design_estimate.m"

            img_filepath_list = populate_filepath_list(l1_images_with_paths,colname)



            create_spm_l2_script(template_filepath, replacement_map = {
                    'OUTDIR': output_folderpath,
                    'img_filepath_list': img_filepath_list,
                    '(MAIN HEADER)': l1_image_name
                    },
                output_filepath = output_filepath
                )
            #now run the script
            #now to texecute, something like
            if execute_l2_script:
                execute_spm_l2_script(output_filepath, spm_path=spm_path)
        else:
            print('contrast ' + l1_image_name + ' not found.')

