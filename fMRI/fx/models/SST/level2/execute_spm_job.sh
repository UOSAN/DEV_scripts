
#!/bin/bash
#--------------------------------------------------------------
# This script executes the matlab script $SCRIPT
#	
#--------------------------------------------------------------

# SPM Path
SPM_PATH=/Users/benjaminsmith/spm12

SCRIPT="/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/models/SST/level2/stop_failed_vs_correct_pp/attempt_20221130/CorrectStop_Post_Minus_Pre_automation_test/CorrectStop_Post_Minus_Pre_contrast_one_sample_design_estimate.m"

echo $SCRIPT
export SCRIPT=$SCRIPT
export SPM_PATH=$SPM_PATH 
bash simple_spm_job.sh