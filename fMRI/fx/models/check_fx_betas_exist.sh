#!/bin/bash

# This script checks that the expected number of beta nifti files 
# (created during first level modeling) exist for each participant.
# Two summary text files are created for each task - one listing subjects that have
# the expected number of betas, and one that lists subjects with missing betas along with
# the number of beta files they acutually have.

# NOTE: run with the bash, rather than sh command
# e.g. `bash check_fx_betas_exist.sh`

echo $BASH_VERSION

# Set paths and tasks
fx_outputdir="/projects/sanlab/shared/REV/bids_data/derivatives/prepost_analysis"
logdir="${fx_outputdir}/logs"
declare -A TASKBETAS=([sst]=64 [gng]=96) # the task(s) to check and its expected number of beta files

# Create directory for log files and the files themselves
if [ ! -d "${logdir}" ]; then
    mkdir -v "${logdir}"
fi

sst_outputlog="${logdir}/extant_fx_files_sst.txt"
sst_errorlog="${logdir}/missing_fx_files_sst.txt"
gng_outputlog="${logdir}/extant_fx_files_gng.txt"
gng_errorlog="${logdir}/missing_fx_files_gng.txt"

touch "${sst_outputlog}" "${sst_errorlog}" "${gng_outputlog}" "${gng_errorlog}"

echo "-------------------Participants WITH all beta maps-------------------" > $sst_outputlog 
echo "-------------------Participants WITH all beta maps-------------------" > $gng_outputlog
echo "-------------------Participants MISSING beta maps-------------------" > $sst_errorlog 
echo "-------------------Participants MISSING beta maps-------------------" > $gng_errorlog

# Check whether each folder has beta maps
cd $fx_outputdir
for subdir in $(ls -d ${fx_outputdir} sub*); do 
    echo "checking" $subdir
    for i in "${!TASKBETAS[@]}"; do
        task=$i
        num_betas=${TASKBETAS[$i]}
        errorlog="${logdir}/missing_fx_files_${task}.txt"
        outputlog="${logdir}/extant_fx_files_${task}.txt"
        if [ -d ${fx_outputdir}/${subdir}/fx ]; then
            echo $subdir > $outputlog_${task}
            path="${fx_outputdir}/${subdir}/fx/${task}"
            cd $path
            shopt -s nullglob
            beta_files=(beta*.nii)
            if (( ${#beta_files[@]} != $num_betas )); then
                echo "${subdir} = ${#beta_files[@]} files, expected $num_betas" >> $errorlog
            else
                echo "${subdir}" >> $outputlog
            fi 
        fi
    done
done

echo "Done. Reports are in ${logdir}"