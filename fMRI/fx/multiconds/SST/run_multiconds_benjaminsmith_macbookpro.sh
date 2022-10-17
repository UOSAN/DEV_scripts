#!/bin/zsh

CONDA_BASE=$(conda info --base)    
echo $CONDA_BASE/etc/profile.d/
source $CONDA_BASE/etc/profile.d/conda.sh

#conda init
cd "/Users/benjaminsmith/Google Drive/oregon/code/DEV_scripts/fMRI/fx/multiconds/SST/"
conda activate level2

python multiconds_full_duration.py --input="/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/Tasks/SST_DEV/output" --output "full_duration"
#this script contains the posterror values as well, and those are useful but unfortunately it's not working right now!
#debug if and when we need them.
#python multiconds_posterror_with_durations.py --input="/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/Tasks/SST_DEV/output" --output "full_duration"
#this one seems to be the working version. use this.
python multiconds_posterror_with_pss.py --input="/Users/benjaminsmith/Dropbox (University of Oregon)/UO-SAN Lab/Berkman Lab/Devaluation/Tasks/SST_DEV/output" --output "full_duration"