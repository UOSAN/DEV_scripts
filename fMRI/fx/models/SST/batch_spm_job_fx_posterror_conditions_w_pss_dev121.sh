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
SPM_PATH=~/spm12

# Set scripts directory path
SCRIPTS_DIR=/Users/bensmith/Documents/code/DEV_scripts

#Set task
TASK=SST

#GET SUBJECTS FILTER FOR SUBJECTS TO CONTRAST AND SUBJECTS TO NOT CONTRAST
SUBJ_TO_CONTRAST=`cat ${SCRIPTS_DIR}/fMRI/fx/multiconds/$TASK/full_duration/posterror_conditions_w_pss/complete_1.txt`
SUBJ_NO_CONTRAST=`cat ${SCRIPTS_DIR}/fMRI/fx/multiconds/$TASK/full_duration/posterror_conditions_w_pss/missing_1.txt`

# Set MATLAB script path
SCRIPT_W_CONTRASTS=${SCRIPTS_DIR}/fMRI/fx/models/$TASK/fx_posterror_conditions_w1_w_pss_dev121.m
SCRIPT_NO_CONTRASTS=${SCRIPTS_DIR}/fMRI/fx/models/$TASK/fx_posterror_conditions_w1_dev121.m


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
# I don't think there separate contrast/non-contrast analyses here?
#for SUB in $SUBJLIST; do
SUB=DEV121
	echo $SUB
	if [[ " ${SUBJ_TO_CONTRAST[*]} " =~ "${SUB}" ]]; then
    	echo "subject $SUB should have a contrast; running $SCRIPT_W_CONTRASTS"
    	echo sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT_W_CONTRASTS,SUB=$SUB,SPM_PATH=$SPM_PATH,  \
		 	--job-name=${RESULTS_INFIX} \
		 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
		 	--cpus-per-task=${cpuspertask} \
		 	--mem-per-cpu=${mempercpu} \
		 	--account=sanlab \
                        --time=30:00 \
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
                        --time=30:00 \
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
                        --time=30:00 \
		 	${SHELL_SCRIPT}
	 	sleep .25
	fi
	
#done

