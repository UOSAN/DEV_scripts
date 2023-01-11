#!/bin/bash

# This script takes the dot product of template maps and subject beta maps. Output is 
# saved as a text file in the output directory.

# Set paths and variables
# ------------------------------------------------------------------------------------------
# variables
maps=$(ls /projects/sanlab/shared/DEV/nonbids_data/rois_patterns/*.nii)
template=/projects/sanlab/shared/DEV/nonbids_data/rois_patterns/craving_regulation_signature.nii
betasALL=`echo $(printf "beta_%04d.nii\n" {1..20}) $(printf "beta_%04d.nii\n" {28..47}) $(printf "beta_%04d.nii\n" {55..74}) $(printf "beta_%04d.nii\n" {82..101})`
betasDEV022=`echo $(printf "beta_%04d.nii\n" {1..20}) $(printf "beta_%04d.nii\n" {28..47}) $(printf "beta_%04d.nii\n" {55..74}) $(printf "beta_%04d.nii\n" {82..89})`
betasDEV060=`echo $(printf "beta_%04d.nii\n" {1..19}) $(printf "beta_%04d.nii\n" {27..46}) $(printf "beta_%04d.nii\n" {54..73}) $(printf "beta_%04d.nii\n" {81..100})`
betasDEV061=`echo $(printf "beta_%04d.nii\n" {1..20}) $(printf "beta_%04d.nii\n" {28..47}) $(printf "beta_%04d.nii\n" {55..73}) $(printf "beta_%04d.nii\n" {81..100})`
betasDEV063=`echo $(printf "beta_%04d.nii\n" {1..20}) $(printf "beta_%04d.nii\n" {28..38}) $(printf "beta_%04d.nii\n" {46..65}) $(printf "beta_%04d.nii\n" {73..92})`
betasDEV082=`echo $(printf "beta_%04d.nii\n" {1..20}) $(printf "beta_%04d.nii\n" {28..42}) $(printf "beta_%04d.nii\n" {50..69}) $(printf "beta_%04d.nii\n" {77..96})`

# paths
image_dir=/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/ROC/wave1/betaseries
output_dir=/projects/sanlab/shared/DEV/DEV_scripts/fMRI/betaseries/ROC/dotProducts_ROC_wave1

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
	if [ $subname == sub-DEV022 ]; then
		betas=$betasDEV022
	elif [ $subname == sub-DEV060 ]; then
		betas=$betasDEV060
	elif [ $subname == sub-DEV061 ]; then
		betas=$betasDEV061
	elif [ $subname == sub-DEV063 ]; then
		betas=$betasDEV063
	elif [ $subname == sub-DEV082 ]; then
		betas=$betasDEV082
	else
		betas=$betasALL
	fi
	for beta in ${betas[@]}; do
		3dAllineate -source ${subdir}/${beta} -master ${template} -final NN -1Dparam_apply '1D: 12@0'\' -prefix ${subdir}/aligned_${beta}
		for map in ${maps[@]}; do
			map_name=$(echo ${map: 79})
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
if [ $subname == sub-DEV022 ]; then
	betas=$betasDEV022
elif [ $subname == sub-DEV060 ]; then
	betas=$betasDEV060
elif [ $subname == sub-DEV061 ]; then
	betas=$betasDEV061
elif [ $subname == sub-DEV063 ]; then
	betas=$betasDEV063
elif [ $subname == sub-DEV082 ]; then
	betas=$betasDEV082
else
	betas=$betasALL
fi
for beta in ${betas[@]}; do
	echo ${SUB} ${beta} `3dBrickStat -mean ${subdir}/${beta}` >> "${output_dir}"/"${SUB}"_meanIntensity.txt
done
done