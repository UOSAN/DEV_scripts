#!/bin/bash
#SBATCH --time 0-0:10:00
#--------------------------------------------------------------
# This script:
#	* Creates a batch job for $SUB
#	* Batch jobs are saved to the path defined in MATLAB script
#	* Executes batch job
#
# D.Cos 2018.11.06
#--------------------------------------------------------------

#load named parameters
while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
        # echo $1 $2 // Optional to see the parameter:value result
   fi

  shift
done

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
matlab -nosplash -nodisplay -nodesktop ${ADDITIONALOPTIONS} -r "clear; addpath('$SPM_PATH'); spm_jobman('initcfg'); sub='$SUB'; subid='$SUBID'; script_file='$SCRIPT'; replacesid='$REPLACESID'; run('make_sid_matlabbatch.m'); spm_jobman('run',matlabbatch); exit"
