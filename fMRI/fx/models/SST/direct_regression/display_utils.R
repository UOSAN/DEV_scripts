

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

pval_asterisks<-function(pval){
  if (is.na(pval)){return(NA)}
  if (pval<0.001){return("***")}
  if (pval<0.01){return("**")}
  if (pval<0.05){return("*")}
  return("")
}

tidy_sq <- function(col){
  if (!is.na(col['Chisq']) & !is.na(col['Pr..Chisq.'])){
    return(paste0(round(col['Chisq'],2),pval_asterisks(col['Pr..Chisq.'])))
  }
  return(col['Chisq'])
}

format_model_comparison <- function(model_comparison){
  anova_raw_result_df <- t(data.frame(model_comparison)[
    ,c("npar", "AIC", "BIC", "logLik" #, "Chisq","Pr..Chisq."
       )])
  
  anova_low_precision<-c( "AIC", "BIC", "logLik")
  #anova_med_precision<-c("Chisq")
  #anova_p_precision<-c("Pr..Chisq.")
  anova_results_tided<-anova_raw_result_df #%>% data.frame()
  anova_results_tided[anova_low_precision,]<-round(anova_results_tided[anova_low_precision,],0)
  #anova_results_tided[anova_med_precision,]<-round(anova_results_tided[anova_med_precision,],2)
  
  #format the p-values
  #anova_results_tided["Chisq",]<-apply(anova_results_tided,2,tidy_sq)

  #anova_results_tided <- anova_results_tided[-which(rownames(anova_results_tided)=='Pr..Chisq.'),]
  return(anova_results_tided)  
  
}

format_combined_table <- function(table_cells){
  table_cells[is.na(table_cells)] <- ""
  table_cells[table_cells=="NA"] <- ""
  return(table_cells)
}

get_chisq_comparisons<-function(model_list, anova_model_order){
  last_model <- anova_model_order[length(anova_model_order)]
  #now compare each of the otehrs against the last model...
  chi_sq_results <- list()
  for (model_i in anova_model_order[-length(anova_model_order)]){
    model_i_vs_last_model <- anova(model_list[[model_i]], model_list[[last_model]])
    model_i_vs_last_model_chisq <- data.frame(model_i_vs_last_model)[2,c("Chisq","Pr..Chisq.")]
    chi_sq_results[[names(model_list)[model_i]]]<-tidy_sq(model_i_vs_last_model_chisq)
    
  }
  chi_sq_results_df <- do.call(rbind,chi_sq_results) %>% data.frame()
  colnames(chi_sq_results_df)<-names(model_list)[last_model]
  return(chi_sq_results_df)
  
}

create_mlm_table_from_model_list <- function(
  model_list,
  name_transform =friendly_name_transform_table,
  table_label = "Median Activity 4-10 s Post-Stop Signal",
  table_footnote = ""
  ){
  fixed_effects_list <- sapply(model_list, custom_mixed_model_summary)
  
  fixed_effects_df <- t(dplyr::bind_rows(fixed_effects_list))
  
  model_comparison <- do.call(anova,unname(model_list))
  
  anova_model_order <- rownames(model_comparison) %>% str_extract("\\d+") %>% as.numeric
  
  
  
  
  anova_results_tided <- format_model_comparison(model_comparison)
  
  #or we can organize the fixed effects in terms of the anova
  #I think that is better...
  fixed_effects_df_anova_order <- fixed_effects_df[,anova_model_order] #%>% data.frame
  
  
  
  #supplementary anovas--we do an anova of all the effects against the best one
  #could do all against all but that would be distracting
  chisq_comparison <- get_chisq_comparisons(model_list, anova_model_order)
  
  table_cells <- rbind(fixed_effects_df_anova_order,anova_results_tided) %>% data.frame()
  #table_cells <- rbind(fixed_effects_df_anova_order,anova_results_tided,chisq_comparison) %>% data.frame()
  
  
  
  
  
  
  table_cells_rownames <- rownames(table_cells)
  for (nt_i in 1:nrow(name_transform)){
    print(nt_i)
    table_cells_rownames <- gsub(name_transform$originalname[nt_i],name_transform$replacementname[nt_i], table_cells_rownames)
  }
  rownames(table_cells)<-table_cells_rownames
  colnames(table_cells)<-names(model_list)[anova_model_order]
  
  table_cells <- bind_rows(table_cells,chisq_comparison)
  
  table_cells <- format_combined_table(table_cells)
  
  model_compare_table <- gt(
    table_cells,
    rownames_to_stub = TRUE) %>%
    tab_stubhead(label="Parameter") %>%
    tab_spanner(
      label=table_label,
      columns = 1:(ncol(table_cells)+1)
    ) %>%
    tab_spanner(
      label="Dependent Variable:",
      columns = 1:(ncol(table_cells)+1)
    ) %>% 
    tab_row_group(
      label = "Chi-square vs.",
      rows = (nrow(table_cells)-nrow(chisq_comparison)+1):nrow(table_cells)
    )%>%
    tab_row_group(
      label = "Fixed effects",
      rows = 1:nrow(fixed_effects_df_anova_order)
    )  %>% 
    row_group_order(groups=c("Fixed effects",NA,"Chi-square vs.")) %>%
    opt_table_font(font="Arial") %>%
    tab_footnote(footnote=table_footnote)
  
  
  
  return(model_compare_table)
  
}

create_sst_mlm_table <- function(
  model_list,
  name_transform =friendly_name_transform_table,
  table_label = "Median Activity 4-10 s Post-Stop Signal",
  table_footnote = "Note: Random effects of Post-Pre RT Change and P(Stop Trial) Change not shown.\nRandom effects were consistent for all models shown in this table."){
  
  return(create_mlm_table_from_model_list(
    model_list,
    name_transform,
    table_label,
    table_footnote
  ))
}
