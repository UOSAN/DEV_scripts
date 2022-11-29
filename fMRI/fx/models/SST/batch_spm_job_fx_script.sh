#!/bin/bash
#--------------------------------------------------------------
# This script executes $SHELL_SCRIPT for $SUB and matlab $SCRIPT
#	
# D.Cos 2018.11.06
#--------------------------------------------------------------

# get this from a value passed in
SCRIPT_NAME=$0





echo '${SCRIPT_NAME}'

## Set your study
STUDY=DEV

# Set subject list
SUBJLIST=`cat subject_list_single_col_wave1.txt`

# Which SID should be replaced?
REPLACESID=004

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts

#Set task
TASK=SST

# Set MATLAB script path
SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/SST/${SCRIPT_NAME}

# Set shell script to execute
SHELL_SCRIPT=spm_job.sh

# RRV the results files
RESULTS_INFIX=fx_conditions

# Set output dir and make it if it doesn't exist
OUTPUTDIR=${SCRIPTS_DIR}/fMRI/fx/models/output_${TASK}_${RESULTS_INFIX}

if [ ! -d ${OUTPUTDIR} ]; then
	mkdir -p ${OUTPUTDIR}
fi

# Set job parameters
cpuspertask=1
mempercpu=8G


# Create and execute batch job
for SUB in $SUBJLIST; do
	echo $SUB
 	echo sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT,SUB=$SUB,SPM_PATH=$SPM_PATH,  \
	 	--job-name=${RESULTS_INFIX} \
	 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
	 	--cpus-per-task=${cpuspertask} \
	 	--mem-per-cpu=${mempercpu} \
	 	--account=sanlab \
        --time=30:00 \
	 	${SHELL_SCRIPT}
 	sleep .25
done
