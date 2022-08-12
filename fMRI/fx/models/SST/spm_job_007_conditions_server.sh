# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

STUDY=DEV

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts

# Set MATLAB script path
SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/SST/fx_conditions_w1_from_spm_test_007.m
SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/SST/fx_conditions_w1_from_spm_test_007.m
# Which SID should be replaced?
REPLACESID=004

SUB=007

#!/bin/bash
#--------------------------------------------------------------
# This script:
#	* Creates a batch job for $SUB
#	* Batch jobs are saved to the path defined in MATLAB script
#	* Executes batch job
#
# D.Cos 2018.11.06
#--------------------------------------------------------------

# set options and load matlab
SINGLECOREMATLAB=true
ADDITIONALOPTIONS=""

if "$SINGLECOREMATLAB"; then
	ADDITIONALOPTIONS="-singleCompThread"
fi

# create and execute job
echo -------------------------------------------------------------------------------
echo "${SUB}"
echo "Running ${SCRIPT}"
echo "Running ${SCRIPT}"
echo "spmpath is $SPM_PATH"
echo -------------------------------------------------------------------------------

module load matlab
matlab -nosplash -nodisplay -nodesktop ${ADDITIONALOPTIONS} -r "clear; addpath('$SPM_PATH'); spm_jobman('initcfg'); sub='$SUB'; script_file='$SCRIPT'; disp('script file:'); disp(script_file); replacesid='$REPLACESID'; run('make_sid_matlabbatch.m'); spm_jobman('run',matlabbatch); exit"
matlab -nosplash -nodisplay -nodesktop ${ADDITIONALOPTIONS} -r "clear; addpath('$SPM_PATH'); spm_jobman('initcfg'); sub='$SUB'; script_file='$SCRIPT'; disp('script file:'); disp(script_file); replacesid='$REPLACESID'; run('make_sid_matlabbatch.m'); spm_jobman('run',matlabbatch); exit"
