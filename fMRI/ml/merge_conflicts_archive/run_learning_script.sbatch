#!/bin/bash

<<<<<<< HEAD
#SBATCH --partition=ctn,long        ### Partition (like a queue in PBS)
=======
#SBATCH --partition=ctn        ### Partition (like a queue in PBS)
>>>>>>> f1fd970dfb9ec5fcfe7b2c2668526e789a921626
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=10G
#SBATCH --time 0-120:00:00
#SBATCH --job-name learningns-16-10g
#SBATCH --output learning-%J.log
#SBATCH --error learning-%J.err
#SBATCH --account=sanlab
 
export CPUS_PER_TASK=$SLURM_CPUS_PER_TASK

module load anaconda3


conda activate neuralsignature
echo "$(date +"%D %T")"
echo "running python script $1"


python $1                        # run your actual program

echo "finished running script $1"
echo "$(date +"%D %T")"
