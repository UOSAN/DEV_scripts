import pandas as pd
from level2_utils import *


# paths
nonbids_data_path = "/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/"
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path = '/Users/benjaminsmith/Google Drive/oregon/preprocessing/DEV_scripts'
ml_scripting_path = dev_scripts_path + "/fMRI/ml"

train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob="/Users/benjaminsmith/Google Drive/oregon/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/posterror_conditions/sub-DEV*/beta_000[1-2].nii",
    nonbids_data_path=nonbids_data_path,
    ml_data_folderpath=ml_data_folderpath,
    ml_scripting_path=ml_scripting_path
)


subject_list = train_betas_with_data.SID.unique()
subject_list.sort()
# we're going to write matlab code in python...
# it's clumsy but effective.
for s_i, s in enumerate(subject_list):
    #for each subject, add a line to the code
    s_index = s_i+1
    print("%" + s)
    print("matlabbatch{1}.spm.stats.factorial_design.des.pt.pair(" + str(s_index) + ").scans = {")
    beta_paths = train_betas_with_data.spm_l2_path_description[train_betas_with_data.SID==s]
    # we need specifically the beta_0001 and then the beta_0002. need to make sure they're in order.
    [re.match("beta\_0001", bp) for bp in beta_paths]

    #ensure our betas are all in order
    for beta_to_match in ['beta_0001','beta_0002']:
        #get the matching path
        beta_path_match = [bp for bp in beta_paths if re.search(beta_to_match,bp) is not None][0]
        #should throw an error if the list is empty.
        #print it
        print("\t" + beta_path_match)
    print("};")




#OK SO WE HAVE GOT THESE, BUT WE REALLY NEED SOMETHING DIFFERENT, BECAUSE WE'RE NOT JUST GRABBING BETA_0002S. WE'RE GRABBING
#BETA_0001.NII AND BETA_0002.NII
#HOWEVER WE STILL PROBABLY WANNA MERGE IN INDIVIDUAL DIFFERNCES FOR MORE ANALYSES.
