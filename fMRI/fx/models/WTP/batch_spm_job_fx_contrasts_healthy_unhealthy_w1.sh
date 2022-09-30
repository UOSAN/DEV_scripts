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
REPLACESID=001

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts

# Set MATLAB script path
SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/WTP/fx_healthy_unhealthy_contrasts_rs.m

# Set shell script to execute
SHELL_SCRIPT=spm_job.sh

# RRV the results files
RESULTS_INFIX=fx_healthy_unhealthy_contrasts_rs

# Set output dir and make it if it doesn't exist
<<<<<<< HEAD
OUTPUTDIR=${SCRIPTS_DIR}/fMRI/fx/models/WTP/fx_healthy_unhealthy_contrasts_rs
=======
OUTPUTDIR=${SCRIPTS_DIR}/fMRI/fx/models/output_${RESULTS_INFIX}
>>>>>>> 3b82b18ca13ec193e63fbc225c6e38231405f27a

if [ ! -d ${OUTPUTDIR} ]; then
	mkdir -p ${OUTPUTDIR}
fi

# Set job parameters
cpuspertask=1
mempercpu=8G

# Create and execute batch job
for SUB in $SUBJLIST; do
	#an ID on its own. need this for certain parts of the script
	SUBID=$(sed "s/DEV//" <<< $SUB)
	#BJS added 2021-06-09
	
 	sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT,SUB=$SUB,SUBID=$SUBID,SPM_PATH=$SPM_PATH,  \
	 	--job-name=${RESULTS_INFIX} \
	 	-o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
	 	--cpus-per-task=${cpuspertask} \
	 	--mem-per-cpu=${mempercpu} \
	 	--account=sanlab \
                --time=30:00 \
	 	${SHELL_SCRIPT}
 	sleep .25
done
