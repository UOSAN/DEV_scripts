#!/bin/bash
#--------------------------------------------------------------
# This script executes $SHELL_SCRIPT for $SUB and matlab $SCRIPT
#	
# D.Cos 2018.11.06
#--------------------------------------------------------------

## Set your study
STUDY=DEV

# Set subject list
SUBJLIST=`cat subject_list_wave1_20220622.txt`

# Which SID should be replaced?
REPLACESID=DEV004

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts

#Set task
TASK=SST

#GET SUBJECTS FILTER FOR SUBJECTS TO CONTRAST AND SUBJECTS TO NOT CONTRAST
SUBJ_TO_CONTRAST=`cat ${SCRIPTS_DIR}/fMRI/fx/multiconds/$TASK/full_duration/posterror_conditions/complete_1.txt`
SUBJ_NO_CONTRAST=`cat ${SCRIPTS_DIR}/fMRI/fx/multiconds/$TASK/full_duration/posterror_conditions/missing_1.txt`

# Set MATLAB script path
SCRIPT_W_CONTRASTS=${SCRIPTS_DIR}/fMRI/fx/models/$TASK/fx_posterror_conditions_w1_w_contrasts.m
SCRIPT_NO_CONTRASTS=${SCRIPTS_DIR}/fMRI/fx/models/$TASK/fx_posterror_conditions_w1.m


# Set shell script to execute
SHELL_SCRIPT=spm_job.sh

# RRV the results files
RESULTS_INFIX=fx_posterror_conditions

# Set output dir and make it if it doesn't exist
OUTPUTDIR=${SCRIPTS_DIR}/fMRI/fx/models/output_${TASK}_${RESULTS_INFIX}

if [ ! -d ${OUTPUTDIR} ]; then
	mkdir -p ${OUTPUTDIR}
fi

# Set job parameters
cpuspertask=1
mempercpu=8G

# Create and execute batch job
# selecting a job based on whether there is adequate data to do a contrast.
for SUB in $SUBJLIST; do
	echo $SUB
	if [[ " ${SUBJ_TO_CONTRAST[*]} " =~ "${SUB}" ]]; then
    	echo "subject $SUB should have a contrast; running $SCRIPT_W_CONTRASTS"
    	sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT_W_CONTRASTS,SUB=$SUB,SPM_PATH=$SPM_PATH,  \
		 	--job-name=${RESULTS_INFIX} \
		 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
		 	--cpus-per-task=${cpuspertask} \
		 	--mem-per-cpu=${mempercpu} \
		 	--account=sanlab \
		 	${SHELL_SCRIPT}
	 	sleep .25
    elif [[ " ${SUBJ_NO_CONTRAST[*]} " =~ "${SUB}" ]]; then
    	echo "subject $SUB should NOT have a contrast; running $SCRIPT_NO_CONTRASTS"
    	sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT_NO_CONTRASTS,SUB=$SUB,SPM_PATH=$SPM_PATH,  \
		 	--job-name=${RESULTS_INFIX} \
		 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
		 	--cpus-per-task=${cpuspertask} \
		 	--mem-per-cpu=${mempercpu} \
		 	--account=sanlab \
		 	${SHELL_SCRIPT}
	 	sleep .25
    else
    	echo "warning for subject $SUB: not in contrast or not contrast list. first-level analysis WITHOUT contrast will be attempted using $SCRIPT_NO_CONTRASTS."
    	sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT_NO_CONTRASTS,SUB=$SUB,SPM_PATH=$SPM_PATH,  \
		 	--job-name=${RESULTS_INFIX} \
		 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
		 	--cpus-per-task=${cpuspertask} \
		 	--mem-per-cpu=${mempercpu} \
		 	--account=sanlab \
		 	${SHELL_SCRIPT}
	 	sleep .25
	fi
	
done

