#!/bin/bash

# This script takes the dot product of template maps and subject beta maps. Output is 
# saved as a text file in the output directory.

# Set paths and variables
# ------------------------------------------------------------------------------------------
# variables
maps=$(ls /projects/sanlab/shared/DEV/nonbids_data/rois_patterns/*.nii)
template=/projects/sanlab/shared/DEV/nonbids_data/rois_patterns/craving_regulation_signature.nii
betas=`echo $(printf "beta_%04d.nii\n" {1..20}) $(printf "beta_%04d.nii\n" {28..47}) $(printf "beta_%04d.nii\n" {55..74}) $(printf "beta_%04d.nii\n" {82..101})`

# paths
image_dir=/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/ROC/wave2/betaseries
output_dir=/projects/sanlab/shared/DEV/DEV_scripts/fMRI/betaseries/ROC/dotProducts_ROC_wave2

if [ ! -d ${output_dir} ]; then
	mkdir -p ${output_dir}
fi

# Calculate dot products
# ------------------------------------------------------------------------------------------
cd ${image_dir}

for subname in $(ls -d sub*); do
	SUB=$(echo ${subname:4:6})
	echo ${SUB}
	subdir=${image_dir}/sub-${SUB}
	
	for beta in ${betas[@]}; do
		3dAllineate -source ${subdir}/${beta} -master ${template} -final NN -1Dparam_apply '1D: 12@0'\' -prefix ${subdir}/aligned_${beta}
		for map in ${maps[@]}; do
			map_name=$(echo ${map: 55})
			echo ${SUB} ${beta} ${map_name} `3ddot -dodot ${subdir}/aligned_${beta} ${map}` >> "${output_dir}"/"${SUB}"_dotProducts.txt
		done
	done
done

# Calculate volume mean intensities
# ------------------------------------------------------------------------------------------
for subname in $(ls -d sub*); do
	SUB=$(echo ${subname:4:6})
	echo ${SUB}
	subdir=${image_dir}/sub-${SUB}

	for beta in ${betas[@]}; do
		echo ${SUB} ${beta} `3dBrickStat -mean ${subdir}/${beta}` >> "${output_dir}"/"${SUB}"_meanIntensity.txt
	done
done
