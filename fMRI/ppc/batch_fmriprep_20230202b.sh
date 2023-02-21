#!/bin/bash
#
# This batch file calls on your subject list (which contains both ID and wave number: SID000,wave1). 
# And runs the job_fmriprep.sh file for each subject. 
# It saves the ouput and error files in specified directories.
#
# Set your directories

container=containers/fmriprep-latest-2018-09-05.simg
freesurferlicense=/projects/sanlab/shared/containers/license.txt
group_dir=/projects/sanlab/shared/ #set path to directory within which study folder lives
study=DEV
study_dir="${group_dir}""${study}"
output_dir="${study_dir}"/"${study}"_scripts/fMRI/ppc/output

if [ ! -d "${output_dir}" ]; then
    mkdir -v "${output_dir}"
fi


# Set subject list
subject_list=`cat new_subject_list_20230202b.txt` 

queue_count=4
# Loop through subjects and run job_mriqc
let subj_count=0
previous_jobs=(0 0 0 0)
for subject in $subject_list; do

  let subj_count++
  let subj_count=($subj_count % $queue_count) #mod the subject count
  
  dcmfolder=`echo $subject|awk '{print $1}' FS=","`
    #this is obsolete
	subid=`echo $subject|awk '{print $2}' FS=","`
	sessid=`echo $subject|awk '{print $3}' FS=","`
	echo $subid, $sessid
	
	#now we will put this batch file in one of three queues, to avoid using too many 
	#computational resources
	echo ${previous_jobs[$subj_count]}
	if [ ${previous_jobs[$subj_count]} -eq 0 ]; then
		job_depend="singleton"
	else
		job_depend="singleton,${previous_jobs[$subj_count]}"
	fi

	echo "$job_depend"
	SBATCH_OUT=$(sbatch --dependency=${job_depend} --export ALL,subid=${subid},sessid=${sessid},group_dir=${group_dir},study_dir=${study_dir},study=${study},container=${container},freesurferlicense=${freesurferlicense} \
		   --job-name fmriprep_${subid} \
		   --partition=ctn \
		   --cpus-per-task=8 \
		   --time=3-00:00:00 \
		   --mem=16G \
		   -o "${output_dir}"/"${subid}"_"${sessid}"_fmriprep_output.txt \
		   -e "${output_dir}"/"${subid}"_"${sessid}"_fmriprep_error.txt \
		   --account=sanlab \
		   job_fmriprep.sh)
	echo $SBATCH_OUT
	#get the jobID for this item
	JOBID=${SBATCH_OUT##* }
	#this is quite the hack, but we're going to put the NEXT
	#job in the queue corresponding to the CURRENT job's jobID
	previous_jobs[$subj_count]=$JOBID
	
done
