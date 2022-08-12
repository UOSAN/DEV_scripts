#!/bin/bash
#SBATCH --partition=ctn       ### Partition (like a queue in PBS)
#SBATCH --job-name=weight_shuffle      ### Job Name
#SBATCH --output=/projects/sanlab/shared/DEV/DEV_scripts/rsfMRI/baseline_analysis/outputs/weight_shuffle.out         ### File in which to store job output
#SBATCH --error=/projects/sanlab/shared/DEV/DEV_scripts/rsfMRI/baseline_analysis/outputs/weight_shuffle.err          ### File in which to store job error messages
#SBATCH --time=0-23:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --cpus-per-task=4               ### Number of CPU needed for the job
#SBATCH --mem=2G              ### Total memory
#SBATCH --account=sanlab      ### Account used for job submission

# Set the environment
module load anaconda3
conda activate dev_rs_env

python /projects/sanlab/shared/DEV/DEV_scripts/rsfMRI/baseline_analysis/scripts/acq_physio_shuffle.py --acq '2' --dv 'Hip_to_Waist_Ratio'