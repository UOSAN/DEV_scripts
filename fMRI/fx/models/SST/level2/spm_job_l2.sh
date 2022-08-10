#!/bin/bash
#SBATCH --partition=short

#--------------------------------------------------------------
# This script:
#	* loads the SPM environment
#	* launches the level  analysis
#--------------------------------------------------------------

# set options and load matlab
SINGLECOREMATLAB=true
ADDITIONALOPTIONS=""

if "$SINGLECOREMATLAB"; then
	ADDITIONALOPTIONS="-singleCompThread"
fi

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

SCRIPT=$1

# execute job
echo -------------------------------------------------------------------------------
echo "Running ${SCRIPT}"
echo "using ${SPM_PATH}"
echo -------------------------------------------------------------------------------


module load matlab
matlab -nosplash -nodisplay -nodesktop ${ADDITIONALOPTIONS} -r "clear; addpath('$SPM_PATH'); spm_jobman('initcfg'); spm('defaults', 'FMRI'); fprintf('asdf');fprintf('$SCRIPT'); spm_jobman('run', '$SCRIPT'); exit"



