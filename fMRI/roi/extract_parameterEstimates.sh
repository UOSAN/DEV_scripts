#!/bin/bash

# This script extracts mean parameter estimates and SDs within an ROI or parcel
# from subject images (e.g. FX condition contrasts). Output is 
# saved as a text file in the output directory.

module load afni

echo -------------------------------------------------------------------------------
echo "${SUB}"
echo "Running ${SCRIPT}"
date
echo -------------------------------------------------------------------------------


# Set paths and variables
# ------------------------------------------------------------------------------------------
# variables
rois=(pgACC vmPFC VS) #roi masks (without file formate, specified below as .nii)
images=(con_0001.nii con_00002.nii) #images to extract parameter estimates from (alt. example: images=`echo $(printf "beta_%04d.nii\n" {1..36}) $(printf "beta_%04d.nii\n" {43..78})`)

# paths
image_dir=/projects/sanlab/shared/study/nonbids_data/fMRI/fx/models/task/wave/modelname/sub-"${SUB}" #fx directory
roi_dir=/projects/sanlab/shared/study/nonbids_data/fMRI/rx/models/task/wave/modelname #roi directory (alt. example: roi_dir=/projects/sanlab/shared/study/bids_data/derivatives/freesurfer/sub-"${SUB}"/mri/fromannots)
output_dir=/projects/sanlab/shared/study/study_scripts/fMRI/roi/parameterEstimates #parameter estimate output directory

if [ ! -d ${output_dir} ]; then
	mkdir -p ${output_dir}
fi

# Align images and extract mean parameter estimates and SDs for each contrast and roi/parcel
# ------------------------------------------------------------------------------------------
for roi in ${rois[@]}; do 
	3dAllineate -source "${roi_dir}"/"${roi}".nii -master "${image_dir}"/mask.nii -final NN -1Dparam_apply '1D: 12@0'\' -prefix "${roi_dir}"/aligned_"${roi}"
	for image in ${images[@]}; do 
	echo "${SUB}" "${image}" "${roi}" `3dmaskave -sigma -quiet -mask "${roi_dir}"/aligned_"${roi}"+tlrc "${image_dir}"/"${image}"` >> "${output_dir}"/"${SUB}"_parameterEstimates.txt
	done
done

