#!/bin/bash
#--------------------------------------------------------------
# This script executes $SHELL_SCRIPT for $SUB and matlab $SCRIPT
#	
# D.Cos 2018.11.06
#--------------------------------------------------------------

## Set your study
STUDY=DEV

# Set subject list
SUBJLIST=`cat subject_list.txt`

# Which SID should be replaced?
REPLACESID=001

# SPM Path
SPM_PATH=/projects/sanlab/shared/spm12

# Set scripts directory path
SCRIPTS_DIR=/projects/sanlab/shared/${STUDY}/${STUDY}_scripts

# Set shell script to execute
SHELL_SCRIPT=spm_job.sh


# Set job parameters
cpuspertask=1
mempercpu=8G

# declare an array of strings representing theese numbers
#strings because this really is just treated as strings; they're not being accessed as numbers
declare -a arr=("0" "2" "4") 

for item in "${arr[@]}"; do

    echo "looping"

    echo $item
    # Set MATLAB script path
    SCRIPT=${SCRIPTS_DIR}/fMRI/fx/models/WTP/fx_betaseries_ns_2s_split_${item}.m

    # RRV the results files
    RESULTS_INFIX=fx_betaseries_ns_2s_split_${item}

    # Set output dir and make it if it doesn't exist
    OUTPUTDIR=${SCRIPTS_DIR}/fMRI/fx/models/output_ns_2s_split_${item}

    if [ ! -d ${OUTPUTDIR} ]; then
        mkdir -p ${OUTPUTDIR}
    fi

    echo $SCRIPT
    echo $RESULTS_INFIX
    echo $OUTPUTDIR


    # Create and execute batch job
    for SUB in $SUBJLIST; do
        #an ID on its own. need this for certain parts of the script
        SUBID=$(sed "s/DEV//" <<< $SUB)

        sbatch --export ALL,REPLACESID=$REPLACESID,SCRIPT=$SCRIPT,SUB=$SUB,SUBID=$SUBID,SPM_PATH=$SPM_PATH,  \
            --job-name=${RESULTS_INFIX} \
            -o ${OUTPUTDIR}/${SUB}_${RESULTS_INFIX}.log \
            --cpus-per-task=${cpuspertask} \
            --mem-per-cpu=${mempercpu} \
            --account=sanlab \
            ${SHELL_SCRIPT}
        sleep .25
    done
    sleep 2
done
