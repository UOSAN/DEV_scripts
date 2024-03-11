import pandas as pd
import os
from glob import glob
from level2_utils import get_data_for_confirmed_train_subjs

# beta_paths = glob("/Users/bensmith/Documents/data/DEV/nonbids_data/fMRI/fx/models/SST/wave1/conditions/sub-DEV*/spmT_0001.nii")

config_data = read_yaml_for_host("l2_config.yml")
# beta_paths = glob(config_data['sst_wave1_path'] + 'conditions/sub-DEV*/beta_0002.nii')


#paths
nonbids_data_path = config_data['nonbids_data_path']
ml_data_folderpath = nonbids_data_path + "fMRI/ml"
dev_scripts_path = config_data['dev_scripts_path']
ml_scripting_path = dev_scripts_path + "/fMRI/ml"



#spmT_0001 is CorrrectGo post failed minus correct stop
train_betas_with_data = get_data_for_confirmed_train_subjs(
    beta_glob = config_data['sst_wave1_path'] + "conditions/sub-DEV*/spmT_0001.nii",
    nonbids_data_path = nonbids_data_path,
    ml_data_folderpath = ml_data_folderpath,
    ml_scripting_path = ml_scripting_path
)

[print(s) for s in train_betas_with_data.spm_output_path_description]

#now we can get out the regressors we want to regress on...
#going to be...
#bf_1
#cancer_promoting_minus_preventing_FFQ
#TESQ_E_suppression
#TESQ_E_sum
#covariates; age and sex
#age365, birthsex
#we will output "sets"--primary variable and covariates
#for each set, we must have
# (a) beta image
# (b) primary variable
# (c) covariates
# with no missing data.

primary_vars = ['SST_PostErrorSlowW1_median']

for pv in primary_vars:
    #os.mkdir(nonbids_data_path + '/fMRI/fx/models/SST/level2' + "/" + pv + "_vars")
    pv_table = train_betas_with_data.loc[:,[pv,#'age365','birthsex',
    'spm_output_path_description']]
    row_is_full = pv_table.isna().any(axis=1)==False
    pv_table_complete = pv_table.loc[row_is_full,:]
    pv_table_complete.to_csv(nonbids_data_path+ 'fMRI/fx/models/SST/level2' + "/" + pv + "_vars.csv")




