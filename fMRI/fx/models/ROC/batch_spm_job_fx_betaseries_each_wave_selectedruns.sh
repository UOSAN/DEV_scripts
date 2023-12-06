#!/bin/bash
#--------------------------------------------------------------
# This script executes $SHELL_SCRIPT for $SUB and matlab $SCRIPT
#	
# D.Cos 2018.11.06
#--------------------------------------------------------------

## Set your study
STUDY=DEV

# Which SID should be replaced?
REPLACESID=DEV001

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts


TASK=ROC

# Set shell script to execute
SHELL_SCRIPT=spm_job_wave_selected_runs.sh

# RRV the results files
RESULTS_INFIX=fx_betaseries

# Set output dir and make it if it doesn't exist
OUTPUTDIR=${SCRIPTS_DIR}/fMRI/fx/models/output/${TASK}_${RESULTS_INFIX}

if [ ! -d ${OUTPUTDIR} ]; then
	mkdir -p ${OUTPUTDIR}
fi

# Set job parameters
cpuspertask=1
mempercpu=8G




for W in 1 2; do
    echo "wave: $W"

    # Set MATLAB script path
    SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/ROC/fx_betaseries_wave_i.m

    # Set subject list
    SUBJLIST="roc_run_data_quality_w${W}_20231206.tsv"


    #set -x

    # Create and execute batch job
    while IFS=$'\t' read -r DEVID SELECTEDRUNS
    do
        #an ID on its own. need this for certain parts of the script
        #SUBID=$(sed "s/DEV//" <<< $SUB)
        #BJS added 2021-06-09
        
        echo "script to run is ${SCRIPT} for $DEVID wave $W for runs $SELECTEDRUNS using ${SHELL_SCRIPT}"
        
        sbatch --export "ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT,SUB=$DEVID,WAVE=$W,SUBID=$DEVID,RUN_JSON=\"${SELECTEDRUNS}\",SPM_PATH=$SPM_PATH"  \
            --job-name=${RESULTS_INFIX} \
            -o ${OUTPUTDIR}/${DEVID}_${RESULTS_INFIX}.log \
            --cpus-per-task=${cpuspertask} \
            --mem-per-cpu=${mempercpu} \
            --account=sanlab \
            ${SHELL_SCRIPT}
        sleep .25
    done < "$SUBJLIST"
done