#!/bin/bash

#SBATCH --partition=interactive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=20G
#SBATCH --time 0-4:00:00
#SBATCH --job-name jupyter
#SBATCH --output jupyter-%J.log
#SBATCH --account=sanlab


sbatch -o get_all_series_log --account=sanlab get_all_series.py