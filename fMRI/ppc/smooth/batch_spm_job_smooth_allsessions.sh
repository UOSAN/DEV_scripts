#!/bin/bash
#--------------------------------------------------------------
# This script executes $SHELL_SCRIPT for $SUB and matlab $SCRIPT
#	
# D.Cos 2018.11.06
#--------------------------------------------------------------

# Set your study scripts folder
STUDY=/projects/sanlab/shared/DEV/DEV_scripts

# Set subject list
SUBJLIST=`cat subject_list_full_20230720.txt`

# Which SID should be replaced?
REPLACESID=DEV001

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



while IFS=',' read -r RAWNAME DEVID WAVENAME
do
    #echo "Column 1: $RAWNAME"
    #echo "Column 2: $DEVID"
    #echo "Column 3: $WAVENAME"
    
	# Set MATLAB script path
	for TASK in ${TASKS[@]}; do
		SCRIPT=${STUDY}/fMRI/ppc/smooth/smooth_${TASK}.m # update script name if applicable
	    echo "script to run is ${SCRIPT}"

		# Run task job
	 	sbatch --dependency=singleton --export ALL,REPLACESID=$REPLACESID,WAVE=$WAVENAME,SCRIPT=$SCRIPT,SUB=$DEVID,SPM_PATH=$SPM_PATH,  \
		 	--job-name=${RESULTS_INFIX}_${DEVID} \
		 	-o ${OUTPUTDIR}/${DEVID}_${RESULTS_INFIX}_${TASK}.log \
		 	--cpus-per-task=${cpuspertask} \
		 	--mem-per-cpu=${mempercpu} \
			--account=sanlab \
			--partition=ctn \
			-t 0-0:30 \
		 	${SHELL_SCRIPT}
	 	sleep .25
	 done
	 
done < "$SUBJLIST"
