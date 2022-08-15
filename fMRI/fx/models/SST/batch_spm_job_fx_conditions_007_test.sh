#!/bin/bash
#--------------------------------------------------------------
# This script executes $SHELL_SCRIPT for $SUB and matlab $SCRIPT
#	
# D.Cos 2018.11.06
#--------------------------------------------------------------

## Set your study
STUDY=DEV

# Set subject list
SUBJLIST=`cat test_subject_list.txt`

# Which SID should be replaced?
REPLACESID=004

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts

# Set MATLAB script path
SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/SST/fx_conditions.m

# Set shell script to execute
SHELL_SCRIPT=spm_job.sh

# RRV the results files
RESULTS_INFIX=fx_conditions

# Set output dir and make it if it doesn't exist
OUTPUTDIR=${SCRIPTS_DIR}/fMRI/fx/models/output

if [ ! -d ${OUTPUTDIR} ]; then
	mkdir -p ${OUTPUTDIR}
fi

# Set job parameters
cpuspertask=1
mempercpu=8G

SUB=DEV007
# Create and execute batch job
#for SUB in $SUBJLIST; do
 	sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT,SUB=$SUB,SPM_PATH=$SPM_PATH,  \
	 	--job-name=${RESULTS_INFIX} \
	 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
	 	--cpus-per-task=${cpuspertask} \
	 	--mem-per-cpu=${mempercpu} \
	 	--account=sanlab \
	 	${SHELL_SCRIPT}
# 	sleep .25
#done
