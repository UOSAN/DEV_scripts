#!/bin/bash
#SBATCH --partition=ctn
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=20G
#SBATCH --time 0-4:00:00
#SBATCH --account=sanlab

echo "loading anaconda"
module load anaconda3
conda activate neuralsignature
python get_all_series_main.py

echo "finished"
#sbatch -o get_all_series_log.out get_all_series_main.py
