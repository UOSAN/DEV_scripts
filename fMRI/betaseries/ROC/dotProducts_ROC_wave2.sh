#!/bin/bash

# This script takes the dot product of template maps and subject beta maps. Output is 
# saved as a text file in the output directory.

# load afni & fsl
module load afni
module load fsl

# Set paths and variables
# ------------------------------------------------------------------------------------------
# variables
maps=$(ls /projects/sanlab/shared/DEV/nonbids_data/rois_patterns/*.nii)

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
betas=$(ls ${subdir}/beta* | rev | cut -c 1-13 | rev)
rm ${subdir}/aligned_*
for map in ${maps[@]}; do
map_name=$(echo ${map: 55})
for beta in ${betas[@]}; do
3dAllineate -source ${subdir}/${beta} -master ${map} -final NN -1Dparam_apply '1D: 12@0'\' -prefix ${subdir}/aligned_${beta}
echo ${SUB} ${beta} `fslhd ${subdir}/${beta} | sed -n '66p' | cut -c 16-`  ${map_name} `3ddot -dodot ${subdir}/aligned_${beta} ${map}` >> "${output_dir}"/"${SUB}"_dotProducts.txt
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
betas=$(ls ${subdir}/beta* | rev | cut -c 1-13 | rev)
for beta in ${betas[@]}; do
echo ${SUB} ${beta} `3dBrickStat -mean ${subdir}/${beta}` >> "${output_dir}"/"${SUB}"_meanIntensity.txt
done
done
