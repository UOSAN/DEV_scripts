#!/bin/bash

#SBATCH --partition=ctn        ### Partition (like a queue in PBS)
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=3
#SBATCH --mem-per-cpu=40G
#SBATCH --time 0-120:00:00
#SBATCH --job-name discrim_3_50g
#SBATCH --output learning-%J.log
#SBATCH --error learning-%J.err
#SBATCH --account=sanlab
 
export CPUS_PER_TASK=$SLURM_CPUS_PER_TASK

module load anaconda3


conda activate neuralsignature
echo "$(date +"%D %T")"
echo "running python script $1"


python $1 "$2" $3                      # run your actual program

echo "finished running script $1"
echo "$(date +"%D %T")"
