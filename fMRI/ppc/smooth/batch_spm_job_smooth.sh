#!/bin/bash
#--------------------------------------------------------------
# This script executes $SHELL_SCRIPT for $SUB and matlab $SCRIPT
#	
# D.Cos 2018.11.06
#--------------------------------------------------------------

# Set your study scripts folder
STUDY=/projects/sanlab/shared/DEV/DEV_scripts

# Set subject list
SUBJLIST=`cat subject_list_single_col_20230210.txt`

# Which SID should be replaced?
REPLACESID=DEV001

# Which wave(s) to run? (e.g. WAVE=1:2 or WAVE=2)
WAVE=2

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set tasks to smooth
TASKS=(ROC WTP SST)

# Set shell script to execute
SHELL_SCRIPT=spm_job.sh

# Tag the results files
RESULTS_INFIX=smooth

# Set output dir and make it if it doesn't exist
OUTPUTDIR=${STUDY}/fMRI/ppc/smooth/output

if [ ! -d ${OUTPUTDIR} ]; then
	mkdir -p ${OUTPUTDIR}
fi

# Set job parameters
cpuspertask=1
mempercpu=1G

# Create and execute batch job
for SUB in $SUBJLIST; do
	
	# Set MATLAB script path
	for TASK in ${TASKS[@]}; do
		SCRIPT=${STUDY}/fMRI/ppc/smooth/smooth_${TASK}.m # update script name if applicable

		# Run task job
	 	sbatch --dependency=singleton --export ALL,REPLACESID=$REPLACESID,WAVE=$WAVE,SCRIPT=$SCRIPT,SUB=$SUB,SPM_PATH=$SPM_PATH,  \
		 	--job-name=${RESULTS_INFIX}_${SUB} \
		 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}_${TASK}.log \
		 	--cpus-per-task=${cpuspertask} \
		 	--mem-per-cpu=${mempercpu} \
			--account=sanlab \
			--partition=ctn \
			-t 0-0:30 \
		 	${SHELL_SCRIPT}
	 	sleep .25
	 done
done
