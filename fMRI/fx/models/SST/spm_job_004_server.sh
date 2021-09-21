## Set your study
STUDY=DEV

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts

# Set MATLAB script path
SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/SST/fx_betaseries_w1_from_spm7.m

# Which SID should be replaced?
REPLACESID=DEV004


SUB=DEV004

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
echo -------------------------------------------------------------------------------

module load matlab
matlab -nosplash -nodisplay -nodesktop ${ADDITIONALOPTIONS} -r "clear; addpath('$SPM_PATH'); spm_jobman('initcfg'); sub='$SUB'; script_file='$SCRIPT'; replacesid='$REPLACESID'; run('make_sid_matlabbatch.m'); spm_jobman('run',matlabbatch); exit"