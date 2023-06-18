#!/bin/bash
#SBATCH --partition=short

#--------------------------------------------------------------
# This script:
#	* Creates a batch job for $SUB
#	* Batch jobs are saved to the path defined in MATLAB script
#	* just runs the script as written.
#	* Executes batch job
#
# D.Cos 2018.11.06
# B SMITH 2022.12.01
#--------------------------------------------------------------

# set options and load matlab
SINGLECOREMATLAB=true
ADDITIONALOPTIONS=""

if "$SINGLECOREMATLAB"; then
	ADDITIONALOPTIONS="-singleCompThread"
fi

# create and execute job
echo -------------------------------------------------------------------------------
echo "Running ${SCRIPT}"
echo -------------------------------------------------------------------------------


MATLAB_PATH=/Applications/MATLAB_R2022a.app/bin/
#module load matlab
$MATLAB_PATH/matlab -nosplash -nodisplay -nodesktop ${ADDITIONALOPTIONS} -r "clear; addpath('$SPM_PATH'); spm_jobman('initcfg'); script_file='$SCRIPT'; run('create_matlabbatch_mat_from_script.m'); spm_jobman('run',matlabbatch); exit"
