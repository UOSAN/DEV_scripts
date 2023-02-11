import os
import json
from pprint import pprint

# Change these to your own paths/times/etc.
bidsdir = os.path.join(os.sep, 'projects', 'sanlab', 'shared', 'DEV', 'bids_data')
include_echo_time = False
echo_time1 = '0.00253'
echo_time2 = '0.00499'


def main():
    subjectdirs = get_subjectdirs()
    for subjectdir in subjectdirs:
        timepoints = get_timepoints(subjectdir)
        for timepoint in timepoints:
            func_dir_path = os.path.join(bidsdir, subjectdir, timepoint, 'func')
            fmap_dir_path = os.path.join(bidsdir, subjectdir, timepoint, 'fmap')
            subj_dir_path = os.path.join(bidsdir, subjectdir)
            if os.path.isdir(func_dir_path):
                func_niftis_partialpath = get_funcdir_niftis(func_dir_path, timepoint)
                if os.path.isdir(fmap_dir_path):
                    fmap_jsons = get_fmap_jsons(fmap_dir_path)
                    write_to_json(func_niftis_partialpath, fmap_jsons, fmap_dir_path, echo_time1, echo_time2, subj_dir_path)
            else:
                continue


def get_subjectdirs() -> list:
    """
    Returns subject directory names (not full path) based on the bidsdir (bids_data directory).

    @rtype:  list
    @return: list of bidsdir directories that start with the prefix sub
    """
    bidsdir_contents = os.listdir(bidsdir)
    has_sub_prefix = [subdir for subdir in bidsdir_contents if subdir.startswith('sub-')]
    subjectdirs = [subdir for subdir in has_sub_prefix if os.path.isdir(os.path.join(bidsdir, subdir))]
    subjectdirs.sort()
    return subjectdirs


def get_timepoints(subject: str) -> list:
    """
    Returns a list of ses-wave directory names in a participant's directory.

    @type subject:  string
    @param subject: subject folder name

    @rtype:  list
    @return: list of ses-wave folders in the subject directory
    """
    subject_fullpath = os.path.join(bidsdir, subject)
    subjectdir_contents = os.listdir(subject_fullpath)
    return [f for f in subjectdir_contents if not f.startswith('.')]


def get_funcdir_niftis(func_dir_path:str, timepoint:str) -> list:
    """
    Returns a list of json files in the func directory.
    """
    func_niftis_partialpath = [os.path.join(timepoint, 'func/', f) for f in os.listdir(func_dir_path) if f.endswith('.nii.gz')]
    return func_niftis_partialpath


def get_fmap_jsons(fmap_dir_path):
    fmap_jsons = [f for f in os.listdir(fmap_dir_path) if f.endswith('.json')]
    return fmap_jsons

def write_to_json(func_niftis_partialpath:list, fmap_jsons:list, fmap_dir_path:str, echo_time1:str, echo_time2:str, subjectdir:str):
    for fmap_json in fmap_jsons:

        json_path = os.path.join(fmap_dir_path, fmap_json)
        # print(json_path)
        # with open(json_path) as target_json_text:
        #     #now target_json as plain text
        #     #open a file and read as plain text
        #     print(target_json_text.read())
        if os.path.getsize(json_path) == 0:
            print("couldn't write data to the following json file because it was empty:")
            print(json_path)
            continue

        #print(fmap_json)
        #print(json_path)
        
        with open(json_path) as target_json:
            #check the size of the file
            


            #now load it as a json file
            json_file = json.load(target_json)
            json_file['IntendedFor'] = func_niftis_partialpath
            if include_echo_time:
                json_file['EchoTime1'] = echo_time1
                json_file['EchoTime2'] = echo_time2

        with open(json_path, 'w') as target_json:
            json.dump(json_file, target_json, indent=4)

    task_file_list=['ROC','WTP','SST','rest']
    # now update the func niftis with tasknames
    for nii_partialpath in func_niftis_partialpath:
        json_partialpath = nii_partialpath.replace('.nii.gz', '.json')
        #print(json_partialpath)
        json_path = os.path.join(subjectdir, json_partialpath)
        with open(json_path) as target_json:
            json_file = json.load(target_json)
            #now add the taskname if this is a task json.
            
            #for each task type, check if this json filename has the task in the name, and if it does, add the 'TaskName' attribute to the json_file
            
            for task_type in task_file_list:
                task_type_str = 'task-' + task_type
                print(task_type)
                #check whether task_type is in json_path filename, excluding the path
                if task_type_str in json_path.split('/')[-1]:
                    #print('updating json file with task name ' + task_type)
                    json_file['TaskName'] = task_type

        with open(json_path, 'w') as target_json:
            json.dump(json_file, target_json, indent=4)


    print(". ", end="")
main()
