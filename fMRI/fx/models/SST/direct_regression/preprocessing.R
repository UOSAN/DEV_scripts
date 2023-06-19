library(tidyverse)
get_df_offset <- function(time_points_c){
  
  
  #get the range of offsets
  min_offset<-round(min(time_points_c$offset))
  max_offset <- round(max(time_points_c$offset))
  
  seq_size <- 0.1
  offset_size<-1
  offset_times <- seq(min_offset,max_offset-max(offset_size,seq_size),seq_size)
  
  dt_list<-list()
  for (cond in unique(time_points_c$condition)){
    print(cond)
    for (ot_i in offset_times){
      #<-offset_times[[20]]
      
      tp_at_offset <- time_points_c %>% filter(offset>=ot_i & offset<(ot_i+offset_size) & condition==cond)
      numeric_cols <- colnames(tp_at_offset)[sapply(tp_at_offset,class)=="numeric"]
      tp_at_offset_m <- data.frame(t(colMeans(tp_at_offset[,numeric_cols],na.rm=TRUE)),check.names=FALSE)
      tp_at_offset_m$offset_start<-ot_i
      tp_at_offset_m$condition<-cond
      dt_list<-append(dt_list,list(tp_at_offset_m))
      if((which(ot_i==offset_times)%%20)==0){
        cat(". ")
      }
      
      
    }
    print("")
    
  }
  df_offset<-data.frame(data.table::rbindlist(dt_list),check.names = FALSE)
  return(df_offset)
}

# 
# # #bernice's code
# mlm_bernice <- function(model_list){
#   # parameters coefficients
#   model_list_tidied <- rep(list(NA),length(model_list))
#   for (i in 1:length(model_list)){
#     model_list_tidied[[i]] <- broom.mixed::tidy(model_list[[i]])
#   }
#   m0_progress<-model_list[[1]]
#   # generate fix effects output dataframe
#   m0_conf = confint(m0_progress)[nrow(confint(m0_progress)),]
#   m0_conf_str <- paste0('[',round(m0_conf[1],2),', ', round(m0_conf[2],2) , ']')
#   fix_output_m0 <- broom.mixed::tidy(m0_progress) %>%
#     mutate(across(c(estimate, statistic), ~ sprintf(.x, fmt = '%#.2f')),
#                                                     p.value = round(p.value, 3),
#                                                     conf.int = c(m0_conf_str, '', '')) %>%
#                     select(term, estimate, conf.int, statistic, df, p.value) %>%
#                     filter(term == “(Intercept)“) %>%
#                     mutate(term = “Intercept”) %>%
#                     select(term, estimate, conf.int)
#                   fix_output_full_progress_6f <- apa_print(full_progress_mlm_6f)$table %>%
#                     mutate(p_num = as.numeric(p.value),
#                            estimate_str = as.character(estimate, keep_label = FALSE)) %>%
#                     mutate(estimate = case_when(p.value == "< .001" ~ paste0(estimate, “***“),
#                               p_num < .05 ~ paste0(estimate, “**“),
#                               p_num <= .1 ~ paste0(estimate, “*”),
#                               TRUE ~ estimate_str)) %>%
#   select(term, estimate, conf.int)
# fix_output_final_progress_6f <- apa_print(final_progress_mlm_6f)$table %>%
#   mutate(p_num = as.numeric(p.value),
#          estimate_str = as.character(estimate, keep_label = FALSE)) %>%
#   mutate(estimate = case_when(p.value == "< .001" ~ paste0(estimate, “***“),
#                                                 p_num < .05 ~ paste0(estimate, “**“),
#                                                 p_num <= .1 ~ paste0(estimate, “*”),
#                                                 TRUE ~ estimate_str)) %>%
#                     select(term, estimate, conf.int)
#                   fix_output_propgress_6f_df <- fix_output_m0 %>%
#                     right_join(fix_output_full_progress_6f, by = “term”) %>%
#                     left_join(fix_output_final_progress_6f, by = “term”)
#                   # variance partition dataframe
#                   obs_n <- as.character(nobs(m0_progress))
#                   gp_n <- as.character(m0_progress@Gp[2])
#                   vars_m0 <-data.frame(insight::get_variance(m0_progress), model = “m0_progress”, observation = obs_n, group = gp_n)
#                   vars_full_progress_6f <- data.frame(insight::get_variance(full_progress_mlm_6f), model = “full_progress_6f”, observation = obs_n, group = gp_n)
#                   vars_final_progress_6f <- data.frame(insight::get_variance(final_progress_mlm_6f), model = “final_progress_6f”, observation = obs_n, group = gp_n)
#                   vars_progress_6f_df <- rbind(vars_m0, vars_full_progress_6f, vars_final_progress_6f) %>%
#                     mutate(ICC = var.random / (var.random + var.residual),
#                            `Marginal R2` = var.fixed / (var.fixed + var.random + var.residual),
#                            `Conditional R2` = (var.fixed + var.random) / (var.fixed + var.random + var.residual)) %>%
#                     select(var.random, var.residual, ICC, `Marginal R2`, `Conditional R2`, observation, group) %>%
#                     mutate(across(var.random:`Conditional R2`, ~ round(.x, 2)))
#                   vars_progress_6f_output_df <- data.frame(t(vars_progress_6f_df), con_1 = “”, con_2 = “”, con_3 = “”) %>%
#                     rownames_to_column(var = “term”) %>%
#                     select(term, MTurkCode, con_1, MTurkCode1, con_2, MTurkCode2, con_3) %>%
#                     setNames(colnames(fix_output_propgress_6f_df))
#                   mlm_progress_6f_apa_df <- rbind(fix_output_propgress_6f_df, vars_progress_6f_output_df)
# }

