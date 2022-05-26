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


#examine the PES figures.
rts$subject_responded <- rts$reaction_time>0
mean_pss_across_trials = rts %>% 
  #select only valid trials and only Go conditions
  filter(trial_number%%2==1) %>% 
  dplyr::group_by(trial_number,subject_responded) %>% summarise(mean_post_stop=mean(pss,na.rm=TRUE))
library(ggplot2)
mean_pss_across_trials <- (
  mean_pss_across_trials %>% mutate(trial_type = dplyr::if_else(subject_responded,true="FailedStop",false="CorrectStop"))
)
ggplot(mean_pss_across_trials,aes(x=trial_number,y=mean_post_stop,color=trial_type))+
  geom_point()+
  geom_smooth(aes(group=trial_type),method="lm",formula="y~x")+
  labs(title = "Post-Stop Slowing: Correct vs Failed Stop",
       subtitle = "slowing in Go Trials following stop trials relative to average of two pre-Stop Go Trials",
       y="mean post stop slowing (s)")

median_pss_across_trials = rts %>% 
  #select only valid trials and only Go conditions
  filter(trial_number%%2==1) %>% 
  dplyr::group_by(trial_number,subject_responded) %>% summarise(median_post_stop=median(pss,na.rm=TRUE))
library(ggplot2)
median_pss_across_trials <- (
  median_pss_across_trials %>% mutate(trial_type = dplyr::if_else(subject_responded,true="FailedStop",false="CorrectStop"))
)
ggplot(median_pss_across_trials,aes(x=trial_number,y=median_post_stop,color=trial_type))+
  geom_point()+
  geom_smooth(aes(group=trial_type),method="lm",formula="y~x")+
  labs(title = "Post-Stop Slowing: Correct vs Failed Stop",
       subtitle = "slowing in Go Trials following stop trials relative to average of two pre-Stop Go Trials",
       y="median post stop slowing (s)")

outlier_trial <- median_pss_across_trials[[which(median_pss_across_trials$median_post_stop>0.15),"trial_number"]]

View(rts[rts$trial_number==outlier_trial &!is.na(rts$pss),])