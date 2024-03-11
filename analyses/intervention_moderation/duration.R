

Sys.setenv(R_CONFIG_ACTIVE = Sys.info()["nodename"])

#install.packages("tidystats")
library(stringr)
library(dplyr)
library(ggplot2)
library(rstatix)
library(data.table)
library(tidyverse)
#source("utils.R")
# data_path <- "../../grant-writing-workshop/files/data/"

# load(paste0(config::get("dev_analysis_data_dir"),"scored_data_w_demographics.RData"))
dropbox_file_dir = config::get("dropbox_data_dir")
# scored<-scored_with_demographics
# rm(scored_with_demographics)
# scored$score <- as.numeric(scored$score)
# scored$scale_name <- sub("-","_",scored$scale_name)

full_dataset_aim3<- readr::read_csv(paste0(dropbox_file_dir,"full_dataset_aim3.csv"))