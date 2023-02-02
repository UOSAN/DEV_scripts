#!/bin/bash

# This script takes the dot product of template maps and subject beta maps. Output is 
# saved as a text file in the output directory.

# load afni
module load afni

# Set paths and variables
# ------------------------------------------------------------------------------------------
# variables
maps=(/projects/sanlab/shared/DEV/nonbids_data/rois_patterns/nsc_koban_2mm.nii) #$(ls /projects/sanlab/shared/DEV/nonbids_data/rois_patterns/*.nii)
betasALL=`echo $(printf "beta_%04d.nii\n" {1..16}) $(printf "beta_%04d.nii\n" {22..37}) $(printf "beta_%04d.nii\n" {43..58}) $(printf "beta_%04d.nii\n" {64..79})`
betasDEV125=`echo $(printf "beta_%04d.nii\n" {1..16}) $(printf "beta_%04d.nii\n" {22..36}) $(printf "beta_%04d.nii\n" {42..57}) $(printf "beta_%04d.nii\n" {63..78})`
betasDEV172=`echo $(printf "beta_%04d.nii\n" {1..16}) $(printf "beta_%04d.nii\n" {22..22}) $(printf "beta_%04d.nii\n" {28..43}) $(printf "beta_%04d.nii\n" {49..64})`
betasDEV234=`echo $(printf "beta_%04d.nii\n" {1..16}) $(printf "beta_%04d.nii\n" {22..29}) $(printf "beta_%04d.nii\n" {35..50}) $(printf "beta_%04d.nii\n" {56..71})`


# paths
image_dir=/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/WTP/wave1/betaseries
output_dir=/projects/sanlab/shared/DEV/DEV_scripts/fMRI/betaseries/WTP/dotProducts_WTP_wave1

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
if [ $subname == sub-DEV125 ]; then
betas=$betasDEV125
elif [ $subname == sub-DEV172 ]; then
betas=$betasDEV172
elif [ $subname == sub-DEV234 ]; then
betas=$betasDEV234
else
betas=$betasALL
fi

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
if [ $subname == sub-DEV125 ]; then
betas=$betasDEV125
elif [ $subname == sub-DEV172 ]; then
betas=$betasDEV172
elif [ $subname == sub-DEV234 ]; then
betas=$betasDEV234
else
betas=$betasALL
fi
for beta in ${betas[@]}; do
echo ${SUB} ${beta} `3dBrickStat -mean ${subdir}/${beta}` >> "${output_dir}"/"${SUB}"_meanIntensity.txt
done
done