#!/bin/bash

# This script runs fmriprep on subjects located in the BIDS directory 
# and saves ppc-ed output and motion confounds
# in the derivatives folder.

# Set bids directories
bids_dir="${group_dir}""${study}"/bids_data
derivatives="${bids_dir}"/derivatives
fmriprep_dir="${derivatives}"/fmriprep_2022
working_dir="${derivatives}"/working/
image="${group_dir}""${container}"

echo -e "\nfMRIprep on ${subid}_${sessid}"
echo -e "\nContainer: $image"
echo -e "\nSubject directory: $bids_dir"
echo -e "fmriprep dir: $fmriprep_dir"
# Source task list
tasks=`cat tasks.txt`

# Load packages
module load singularity

# Create working directory
#echo "creating dir $working_dir"`
mkdir -p $working_dir

# Run container using singularity
cd $bids_dir

#create a temp dir just for this job
#job_tempdir=${USER}_${study}_${subid}_${sessid}

export JOBDIR=${USER}_${study}_${subid}_${sessid}_${SLURM_JOB_ID}
export TMPPATH=/gpfs/projects/sanlab/shared/DEV/nonbids_data/tmp/$JOBDIR

mkdir -p ${TMPPATH}

#mkdir -p /tmp/${job_tempdir}
#creating a temp dir for the specific job prevents this job from interfering with other job's temp files
#in the event they're running simultaneously

for task in ${tasks[@]}; do
	echo -e "\nStarting on: $task"
	echo -e "\n"

	PYTHONPATH="" singularity run --bind "${group_dir}":"${group_dir}" --bind ${TMPPATH}:"/tmp/$JOBDIR" $image $bids_dir $fmriprep_dir participant \
		--participant_label $subid \
		-t $task \
		-w "/tmp/$JOBDIR" \
		--output-space {T1w,MNI152NLin2009cAsym,fsaverage,fsnative} \
		--nthreads 4 \
		--mem-mb 16000 \
		--fs-license-file $freesurferlicense \
		--ignore slicetiming \
		--longitudinal


	echo -e "\n"
	echo -e "\ndone"
	echo -e "\n-----------------------"
done

/usr/bin/rm -rvf ${TMPPATH} 
# clean tmp folder
#/usr/bin/rm -rvf /tmp/${job_tempdir}
##/usr/bin/rm -rvf /tmp/${job_tempdir}/fmriprep*
