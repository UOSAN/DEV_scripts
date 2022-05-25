library("readr")
library("dplyr")
rts <- read_csv("/Users/bensmith/Documents/code/DEV_scripts/fMRI/fx/multiconds/SST/full_duration/posterror_conditions_w_rt_multicond_out.csv")

mean_rt_across_trials = rts %>% 
  #select only valid trials and only Go conditions
  filter(trial_number%%2==1 & go_no_go_condition==0) %>% 
  dplyr::group_by(trial_number) %>% summarise(mean_rt=mean(reaction_time))
plot(mean_rt_across_trials)

table(rts$go_no_go_condition,rts$subject_response)

subject_mean_response = rts %>% 
  #select only valid trials and only Go conditions
  filter(trial_number%%2==1 & go_no_go_condition==0) %>% 
  dplyr::group_by(subject_id) %>% summarise(subj_mean_rt=mean(reaction_time))


mean_rt_deviation_across_trials = merge(rts,subject_mean_response) %>% 
  #select only valid trials and only Go conditions
  filter(trial_number%%2==1 & go_no_go_condition==0) %>% 
  dplyr::group_by(trial_number) %>% summarise(mean_rt_deviation=mean(reaction_time-subj_mean_rt))
plot(mean_rt_deviation_across_trials)