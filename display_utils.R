

present_estimate_with_std_error<-function(coef_row,dp=2){
  return(paste0(
    as.character(round(coef_row[["Estimate"]],dp)), " (", 
    as.character(round(coef_row[["Std. Error"]],dp)), ")"
  ))
}

custom_mixed_model_summary<-function(model){
  m_summary <- summary(model)
  fixed_effects = apply(m_summary$coefficients,1,present_estimate_with_std_error)
  return(fixed_effects)
}

format_model_comparison <- function(model_comparison){
  anova_raw_result_df <- t(data.frame(model_comparison)[,c("npar", "AIC", "BIC", "logLik", "Chisq","Pr..Chisq.")])
  
  anova_low_precision<-c( "AIC", "BIC", "logLik")
  anova_med_precision<-c("Chisq")
  anova_p_precision<-c("Pr..Chisq.")
  anova_results_tided<-anova_raw_result_df #%>% data.frame()
  anova_results_tided[anova_low_precision,]<-round(anova_results_tided[anova_low_precision,],0)
  anova_results_tided[anova_med_precision,]<-round(anova_results_tided[anova_med_precision,],2)
  anova_results_tided[anova_p_precision,]<-format.pval(anova_results_tided[anova_p_precision,])
  
  #anova_result_df_input_order <- do.call(rbind, anova_reorganized_list)
  
  
  
  
  return(anova_results_tided)  
  
}

format_combined_table <- function(table_cells){
  table_cells[is.na(table_cells)] <- ""
  return(table_cells)
}

create_mlm_table_from_model_list <- function(model_list){
  fixed_effects_list <- sapply(model_list, custom_mixed_model_summary)
  
  fixed_effects_df <- t(dplyr::bind_rows(fixed_effects_list))
  
  model_comparison <- do.call(anova,unname(model_list))
  
  anova_model_order <- rownames(model_comparison) %>% str_extract("\\d+") %>% as.numeric
  
  
  anova_results_tided <- format_model_comparison(model_comparison)
  
  #or we can organize the fixed effects in terms of the anova
  #I think that is better...
  fixed_effects_df_anova_order <- fixed_effects_df[,anova_model_order] #%>% data.frame
  
  table_cells <- rbind(fixed_effects_df_anova_order,anova_results_tided) 
  
  
  
  table_cells <- format_combined_table(table_cells)
  return(table_cells)
  
}