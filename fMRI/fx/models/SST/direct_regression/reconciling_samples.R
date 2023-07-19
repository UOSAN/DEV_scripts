library(tidyverse)
Sys.setenv(R_CONFIG_ACTIVE = Sys.info()["nodename"])
print(Sys.info()["nodename"])
library(stargazer)
library(tidyverse)
library(gt)
source("preprocessing.R")
source("display_utils.R")


contrast_dataset_raw <- readr::read_csv(paste0(config::get("dev_scripts_path"),"fMRI/fx/models/SST/level2/posterror_cues_no_rt_20230616/raw_filelist.csv"))

load(paste0(dropbbox_dir, "ppt_list_w_data.RData"))

cache_filepath <- paste0(dropbbox_dir,"sst_paper_generation_w12.Rdata")

load(cache_filepath)

modeling_set_subids <- unique(time_points$subid)
modeling_set_subids_w1 <- sort(unique(time_points %>% filter(wave==1) %>% .$subid))




