#!/bin/bash

# This script takes the dot product of template maps and subject beta maps. Output is 
# saved as a text file in the output directory.

# load afni
module load afni

# Set paths and variables
# ------------------------------------------------------------------------------------------
# variables
maps=(/projects/sanlab/shared/DEV/nonbids_data/rois_patterns/nsc_koban_2mm.nii) #$(ls /projects/sanlab/shared/DEV/nonbids_data/rois_patterns/*.nii)
betas=`echo $(printf "beta_%04d.nii\n" {1..16}) $(printf "beta_%04d.nii\n" {22..37}) $(printf "beta_%04d.nii\n" {43..58}) $(printf "beta_%04d.nii\n" {64..79})`

# paths
image_dir=/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/WTP/wave2/betaseries
output_dir=/projects/sanlab/shared/DEV/DEV_scripts/fMRI/betaseries/WTP/dotProducts_WTP_wave2

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

rm ${subdir}/aligned_*
for map in ${maps[@]}; do
map_name=$(echo ${map: 55})
for beta in ${betas[@]}; do
3dAllineate -source ${subdir}/${beta} -master ${map} -final NN -1Dparam_apply '1D: 12@0'\' -prefix ${subdir}/aligned_${beta}
echo ${SUB} ${beta} ${map_name} `3ddot -dodot ${subdir}/aligned_${beta} ${map}` >> "${output_dir}"/"${SUB}"_dotProducts.txt
done
rm ${subdir}/aligned_*
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