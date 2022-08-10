#!/bin/bash
#SBATCH --account=ctn   ### change this to your actual account for charging
#SBATCH --partition=sanlab       ### queue to submit to
#SBATCH --job-name=data_extract    ### job name
#SBATCH --output=logs/%x_job%j.out   ### file in which to store job stdout
#SBATCH --error=logs/%x_job%j.err    ### file in which to store job stderr
#SBATCH --time=60                ### wall-clock time limit, in minutes
#SBATCH --mem=100000M              ### memory limit per node, in MB

echo 'starting script'

module load anaconda3
conda activate neuralsignature

python extract_raw_finger_data_crudehrf.py
