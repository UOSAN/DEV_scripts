# This script loads the fmriprep confound files, applies a machine learning classifier to 
# predict motion artifacts, and returns summaries by task, task and run, and trash volumes only. 
# It will also export new rp_txt files if writeRP = TRUE and plots if writePlots = TRUE.

# Inputs:
# * config.R = configuration file with user defined variables and paths

# Outputs:
# * study_summaryRun.csv = CSV file with summary by task and run
# * study_summaryTask.csv = CSV file with summary by task only
# * study_trashVols.csv = CSV file with trash volumes only
# * if writeRP = TRUE, rp_txt files will be written to rpDir
# * if writePlots = TRUE, plots for each subjects will be written to plotDir
#
motion_get_packages()


#------------------------------------------------------
# source the config file
#------------------------------------------------------
cat("loading config...")
source('config.R')
cat("config loaded.\n")
#------------------------------------------------------
# load confound files
#------------------------------------------------------
source("auto_motion_fmriprep_files.R")
dataset <- motion_prep_load()

motion_classify_summarize_write(dataset)

if (file.exists(state_filename)) {
  #Delete file if it exists
  file.remove(state_filename)
}
