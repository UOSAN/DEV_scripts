from sklearn.inspection import permutation_importance
from ml_util import IndependentVarStratifiedKFold
import numpy as np
import pandas as pd
from IPython.display import display, HTML
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn import linear_model
from ml_util import get_data_for_imputation
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.inspection import permutation_importance

import matplotlib.pyplot as plt


def generate_synthetic_dev_outcomes(outcome_measures):
    #set np random seed
    np.random.seed(3161526)

    #rename columns to what we'll expect once we have the wave 2 data in
    outcome_measures.rename(columns={
        'cancer_promoting_minus_preventing_FFQ':'cancer_promoting_minus_preventing_FFQ_w1','FFQ_v2_Mean_Energy':'FFQ_v2_Mean_Energy_w1'}, inplace=True)

    #add a random drift of 1.0 to each of these...
    def add_rnd_drift(datacol):
        return(datacol + np.random.normal(0,np.std(datacol)/2,len(datacol)))


    outcome_measures['bf_2']=add_rnd_drift(outcome_measures.bf_1)
    outcome_measures['cancer_promoting_minus_preventing_FFQ_w2']=add_rnd_drift(outcome_measures.cancer_promoting_minus_preventing_FFQ_w1)
    outcome_measures['FFQ_v2_Mean_Energy_w2']=add_rnd_drift(outcome_measures.FFQ_v2_Mean_Energy_w1)
    return(outcome_measures)



def generate_synthetic_dev_data(analysis_data_imputed, group_assignments, outcome_measures, group_interaction_effects = None):
    """
        This function generates synthetic data for the intervention moderation analysis.
        It takes in the imputed data, the group assignments, and the outcome measures.
        It also takes in a dictionary of predictor interaction effects.
        The dictionary should have the following structure:
        group_interaction_effects = {'group_name': list_of_effect_sizes}
        where list_of_effect_sizes is a list of effect sizes for each predictor and should have a length equal to the number of predictors.
    """

    #make a copy of the outcome measures
    #don't want to modify the original
    outcome_measures=outcome_measures.copy()
    np.random.seed(3201203)

    #create a normed version of the predictor array
    #normalize each column to have mean 0 and std 1
    predictors_normed = analysis_data_imputed.copy()
    for col in predictors_normed.columns:
        predictors_normed[col] = (predictors_normed[col] - np.mean(predictors_normed[col]))/np.std(predictors_normed[col])




    #sample effect size from a normal distribution for each predictor
    #sample from a normal distribution with mean 0 and std 0.1
    #then add to the predictor value
    #for each group, calculate main effect
    groups = np.unique(group_assignments)[1:]
    print(groups)
    group_main_effects = np.random.normal(0,1,groups.shape[0])
    print(group_main_effects)


    #apply the main effect. note that the first group will not have a main effect
    for i,group in enumerate(groups):
        for om in ['bf_2','cancer_promoting_minus_preventing_FFQ_w2','FFQ_v2_Mean_Energy_w2']:
            om_mean = np.nanmean(outcome_measures[om])
            om_sd = np.nanstd(outcome_measures[om])
            outcome_measures[om] = outcome_measures[om] + (group_assignments==group)*group_main_effects[i]

    interaction_effects_list = []
    print(group_assignments)
    #apply the interaction effect
    for i,group in enumerate(groups):
        print(group)
        #generate interaction effect for group
        #check to see if there are pre-defined interaction effects for this group
        if group_interaction_effects is None:
            predictor_interaction_effects = np.random.normal(0,0.5,predictors_normed.shape[1])
        elif group in group_interaction_effects.keys():
            predictor_interaction_effects = group_interaction_effects[group]
        else:
            predictor_interaction_effects = np.random.normal(0,0.5,predictors_normed.shape[1])

        #print some of the fake effects we're generating
        effect_summary = pd.DataFrame(
            {'feature_name':analysis_data_imputed.columns,
            'interaction_effect':predictor_interaction_effects})
        effect_summary['interaction_effect_abs'] = np.abs(effect_summary.interaction_effect)
        effect_summary = effect_summary.sort_values('interaction_effect_abs',ascending=False)
        print(effect_summary.iloc[0:20,0:2])
        #just add an effect of 1 to the first item only.
        # predictor_interaction_effects = [0]*(predictors_normed.shape[1])
        # predictor_interaction_effects[i] = 0.5
        # print(predictor_interaction_effects[0:10])
        #multiply the predictor interaction effect by the predictor values
        predictor_interaction_values = predictors_normed * predictor_interaction_effects
        # print(predictor_interaction_values.iloc[0:10,0:5])
        outcome_zscore_change = (group_assignments==group)*np.sum(predictor_interaction_values,axis=1)
        # print("zscore:")
        # print(outcome_zscore_change.head())
        # #add that to the outcome measures
        for om in ['bf_2','cancer_promoting_minus_preventing_FFQ_w2','FFQ_v2_Mean_Energy_w2']:
            #take mean and sd of non-nan values
            print(om)
            om_mean = np.nanmean(outcome_measures[om])
            om_sd = np.nanstd(outcome_measures[om])
            # print(om_mean)
            # print(om_sd)
            
            outcome_measures.loc[group_assignments==group,om] = outcome_measures.loc[group_assignments==group,om] + outcome_zscore_change[group_assignments==group]*om_sd

        
        interaction_effects_list.append(
            pd.DataFrame(
            {'group':[group]*predictors_normed.shape[1],
            'predictor':predictors_normed.columns,
            'interaction_effect':predictor_interaction_effects})
        )


        interaction_effect_df = pd.concat(interaction_effects_list)

        interaction_effect_abs = np.abs(interaction_effect_df.interaction_effect)
        #sort by absolute value of interaction effect
        interaction_effect_df['interaction_effect_abs'] = interaction_effect_abs
        interaction_effect_df = interaction_effect_df.sort_values('interaction_effect_abs',ascending=False)
        interaction_effect_df = interaction_effect_df.drop('interaction_effect_abs',axis=1)

    return({'X_weights':interaction_effect_df,'y':outcome_measures})    



def set_up_interactions(predictor_data, group_assignment_onehots):
    #predictor_data = analysis_data_imputed
    predictor_data_columns = predictor_data.columns
    predictor_data_array = np.array(predictor_data)
    predictor_data = pd.concat([predictor_data,group_assignment_onehots],axis=1)
    for group_name in group_assignment_onehots.columns:

        #do a matrix multiplication of the group assignment onehot with the analysis data
        #repeat the group assignment onehot for each column in the analysis data
        
        interaction_array = predictor_data_array*np.array(group_assignment_onehots[group_name],ndmin=2).T
        interaction_df = pd.DataFrame(interaction_array, columns= [(c + '*'+group_name) for c in predictor_data_columns])
        print(interaction_df.shape)
        #then add the result to the analysis data
        predictor_data = pd.concat([predictor_data,interaction_df],axis=1)

    return(predictor_data)
    
    

def do_scoring_loop(X, y, groups,hyperparameter_selection_on_fold,outer_folds):
  outer_splits = outer_folds
  inner_splits = outer_splits - 1

  outer_cv = IndependentVarStratifiedKFold(independent_vars=groups, n_splits=outer_splits, shuffle=True, random_state=3211050)
  #hold up. how does cross_val_score manage with an outer and inner CV that are defined at the same time?
  #maybe it doesn't matter.



  scores = []

  best_models = []
  best_params_df_list = []
  raw_cv_results_list = []
  # now do cv.split and print the items in each fold
  for i, (train_i, test_i) in enumerate(outer_cv.split(X, y)):
      print("outer split" + str(i))

      #test to see if this works on the group assignments
      # print("train:"+ str(dict(pd.Series(groups[train_i]).value_counts())) + ", " + 
      #       "test:" + 
      #     str(dict(pd.Series(groups[test_i]).value_counts()))
      # )

      train_i_X = X.iloc[train_i]
      train_i_y = y.iloc[train_i]
      train_i_group_assignments = groups[train_i]
      #print(train_i_y)

      test_i_X = X.iloc[test_i]
      test_i_y = y.iloc[test_i]
      #print(test_i_y)

      inner_cv = IndependentVarStratifiedKFold(independent_vars=train_i_group_assignments, n_splits=inner_splits, shuffle=True, random_state=3211050)

      selection_info = hyperparameter_selection_on_fold(train_i_X, train_i_y,cv = inner_cv)
      best_model_i = selection_info['best_model']
      best_params_i = selection_info['best_params_df']
      best_models.append(best_model_i)
      best_params_df_list.append(best_params_i)
      raw_cv_results_list.append(selection_info['raw_cv_results'])

      best_model_i.fit(train_i_X, train_i_y)
      score_r2_i = best_model_i.score(test_i_X, test_i_y)

      scores.append(score_r2_i)

  return({
      'scores':scores,
      'best_models':best_models,
      'best_params_df_list':best_params_df_list,
      'raw_cv_results_list':raw_cv_results_list
  })


def summarize_overall_df_results(raw_cv_results_list):
    cv_results_list = []
    for i, raw_result_fold_i in enumerate(raw_cv_results_list):
        for gsm in raw_cv_results_list[i]:
            gsm_j_cv_results_df = pd.DataFrame(gsm.cv_results_)
            gsm_j_cv_results_df['fold'] = i
            gsm_j_cv_results_df['model_description'] = str(gsm.estimator.named_steps.values())
            gsm_j_cv_results_df['model'] = gsm.estimator
            
            cv_results_list.append(gsm_j_cv_results_df)

    cv_results_df = pd.concat(cv_results_list)
    cv_results_df['params_str'] = cv_results_df['params'].astype(str)
    return(cv_results_df)


def get_best_model(cv_results_df):
    #group by model_description and params across folds and get the mean and std of the mean and std test scores
    performance_list = (
        cv_results_df
    .groupby(['model_description','params_str'])
    .agg({'mean_test_score':['mean','std'],'std_test_score':['mean','std']})
    )

    list_model_performance = (performance_list
    .sort_values(('mean_test_score','mean'),ascending=False)
    )

    #print the list in an html format that will look pretty in jupyter
    display(HTML(list_model_performance.to_html()))

    overall_fits =  performance_list.reset_index()

    #identify the index of best fit
    best_fit_description = overall_fits[overall_fits[('mean_test_score','mean')]==overall_fits[('mean_test_score','mean')].max()]

    best_fit_characteristics =  cv_results_df.loc[((cv_results_df['model_description']==best_fit_description['model_description'].values[0]) & 
                   (cv_results_df['params_str']==best_fit_description['params_str'].values[0])),:].iloc[0]
    
    best_model = clone(best_fit_characteristics.model)
    best_model_params = best_fit_characteristics.params
    best_model.set_params(**best_model_params)
    return(best_model)

    

def do_final_fit(X,y,final_model):
    final_fit = final_model.fit(X,y)
    
    return(final_fit)

def present_model_results(X,y, final_fit):
    final_estimator = final_fit.named_steps['estimator']
    
    if hasattr(final_estimator,'coef_'):
        coef = final_estimator.coef_
    else:
        coef = None

    #now check to see if there was a feature selection step,
    #if so, get the feature names from the feature selection step
    if 'feature_selection' in final_fit.named_steps:
        feature_bool = final_fit.named_steps['feature_selection'].get_support(indices=True)
    else:
        feature_bool = [True]*len(X.columns)
    
    feature_names = X.columns[feature_bool]

    #now do a permutation test to do feature importance
    #view the coefficients
    print("doing permutation test on importance; this may take time.")
    permutation_res= [im for im in permutation_importance(final_fit, X, y, n_repeats=10).importances_mean]
    # print(len(feature_names))
    # print(len(permutation_res))
    # print(len(coef))
    
    
    final_results = pd.DataFrame({
        'predictor': feature_names,
        'coef': coef,
        'feature_importance':pd.Series(permutation_res)[feature_bool]
        #'std_err': np.sqrt(np.diag(model_fit.coef_cov_)),
        #'pval': 2*(1-stats.t.cdf(np.abs(model_fit.coef_/np.sqrt(np.diag(model_fit.coef_cov_))),df=predictor_data_nona.shape[0]-predictor_data_nona.shape[1]))
    })

    final_results['fa_abs'] = np.abs(final_results.feature_importance)
    final_results = final_results.sort_values('fa_abs',ascending=False)

    if coef is not None:
        selected_features_count = np.sum(final_estimator.coef_!=0)
        print(f"Number of selected features: {selected_features_count}")

    display(HTML(final_results[0:20].to_html()))
    return(final_results)

def present_results_vs_ground_truth_cors(predictor_data_nona,outcome_measures_nona,group_assignments_nona,final_results,base_regressors):

    group_correlation_list = []
    for group_name in ['ichi','ni','san']:

        #print(group_name)
        group_data = predictor_data_nona.loc[group_assignments_nona==group_name,:]
        group_outcomes = outcome_measures_nona.loc[group_assignments_nona==group_name,'d_bf']

        
        
        #get the two-way correlation between data and the outcome column
        #these are what was actually modeled into the data.
        group_correlations = pd.DataFrame({group_name + '_cor':group_data[base_regressors].corrwith(group_outcomes)})
        #print(group_correlations)
        group_correlation_list.append(group_correlations)

    #concatenate the group correlations into a single dataframe
    group_correlations = pd.concat(group_correlation_list,axis=1)
    
    interaction_effect_labels = final_results.predictor.str.split("*",expand=True)
    interaction_effect_labels.columns = ['measure','group']

    #if the group column is empty, then it's a base effect. label it as such
    interaction_effect_labels.loc[interaction_effect_labels['group'].isna(),'group'] = 'base'

    #add the interaction effect labels to the final results
    final_results = pd.concat([final_results,interaction_effect_labels],axis=1)

    # reshape to wide format, with the group column as header adn coef as the values
    if np.any([x is not None for x in final_results.coef]):
        final_results_wide = final_results.pivot(index='measure',columns='group',values=['coef','feature_importance'])
        #merge the wide format with the group correlations
        #rows won't be in the same order so need to match the index names
        results_vs_cors = final_results_wide.merge(group_correlations, left_index=True, right_index=True, how='outer')
        
        #do a row sum of absolute values
        feature_cols = [x for x in results_vs_cors.columns if x[0]=='feature_importance' and x[1] in ['base','ni','san']]
    else:
        final_results_wide = final_results.pivot(index='measure',columns='group',values=['feature_importance'])
        #merge the wide format with the group correlations
        #rows won't be in the same order so need to match the index names
        results_vs_cors = final_results_wide.merge(group_correlations, left_index=True, right_index=True, how='outer')
        
        #do a row sum of absolute values
        feature_cols = [x for x in results_vs_cors.columns if x in ['base','ni','san']]
        
    results_vs_cors['abs_effect_sum'] = np.sum(np.abs(results_vs_cors[feature_cols]),axis=1)
        


    #sort by the absolute effect sum
    results_vs_cors.sort_values(by='abs_effect_sum',ascending=False,inplace=True)

    #get the number of the last row with a non-na correlation
    not_na_values = (~results_vs_cors['ichi_cor'].isna()).reset_index(drop=True)
    last_not_na = not_na_values[not_na_values].index[-1]

    #get the number of the last row with a non-zero effect

    not_zero_values = (results_vs_cors['abs_effect_sum']>0.001).reset_index(drop=True)
    if np.any(not_zero_values)==False:
        last_not_zero = last_not_na
    else:
        last_not_zero = not_zero_values[not_zero_values].index[-1]

    last_line = np.min([last_not_na,last_not_zero])

    #print as HTML
    display(HTML(np.round(results_vs_cors.iloc[0:last_line+1,:],3).to_html()))

    return({
        'results_vs_cors':results_vs_cors,
        'group_correlations':group_correlations,
        'final_results_wide':final_results_wide
    })


def load_and_preprocess_data(dropbox_data_dir):
    """
    Load the data and preprocess it
    does not include imputing data

    """

    data_by_ppt_path = dropbox_data_dir + '/data_by_ppt.csv'
    data_codebook_path = dropbox_data_dir + 'data_codebook.csv'

    data_by_ppt = pd.read_csv(data_by_ppt_path)
    data_codebook = pd.read_csv(data_codebook_path)

    #find out which columns in data_by_ppt are missing from the codebook
    data_by_ppt.columns.difference(data_codebook['VarName'])


    #copy our outcome measures, bf_1 and FFQ_1, into a new dataframe
    data_by_ppt['bf_2'] = data_by_ppt.bf_1
    #need to decide what sort of FFQ we want to use
    data_by_ppt['cancer_promoting_minus_preventing_FFQ_1'] = data_by_ppt.cancer_promoting_minus_preventing_FFQ
    data_by_ppt['cancer_promoting_minus_preventing_FFQ_2'] = data_by_ppt.cancer_promoting_minus_preventing_FFQ

    # do a report on missing data
    analysis_data  = data_by_ppt.loc[:,data_codebook.loc[data_codebook.IsSelectedPredictor,"VarName"]].copy()
    outcome_measures = data_by_ppt.loc[:,data_codebook.loc[data_codebook.IsSelectedOutcomeMeasure,"VarName"]].copy()

    na_values = pd.DataFrame(data_by_ppt.isna().sum())
    na_values.columns = ['NA_Count']
    na_values['prop_NA'] = na_values.NA_Count / data_by_ppt.shape[0]
    data_codebook = data_codebook.merge(na_values, left_on='VarName', right_index=True)

    data_codebook.to_csv(dropbox_data_dir + 'data_metadata.csv', index=False)

    one_hot_vals = pd.get_dummies(analysis_data.birthsex_factor)
    #there's only two variables here so we can convert this into a dummy variable
    analysis_data.drop(columns=['birthsex_factor'], inplace=True)
    one_hot_vals.columns = ['birthsex_factor_' + str(col) for col in one_hot_vals.columns]
    analysis_data = analysis_data.join(one_hot_vals.iloc[:,1:])
    return(analysis_data, outcome_measures)


def impute_data(analysis_data,graph_against_col=None):
    """
    Does data imputing. Should not be used for a final analysis, because
    imputing of data should occur within the pipeline, so has not to permit data leakage
    """

    imputer = IterativeImputer(estimator=linear_model.Ridge(),n_nearest_features=10,max_iter=100,random_state=0)
    analysis_data_imputed = get_data_for_imputation(analysis_data)

    #this dataset is already filtered for columns so we don't need to filter those further.
    analysis_data_imputed = pd.DataFrame(imputer.fit_transform(analysis_data_imputed), columns=analysis_data_imputed.columns)
    imputed_datapoint = analysis_data.isna()
    # do_aces_cses_imputation_diagnostic(analysis_data_imputed, imputed_datapoint,'ridge_10')
    if graph_against_col is not None:
        cols_with_imputed_data = analysis_data_imputed.columns[analysis_data_imputed.isna().sum()>0]
        for i, col in enumerate(cols_with_imputed_data):
            #get a column indicating whether each point in this column was imputed
            imputed_datapoint = imputed_datapoint[col]
            #plot a scatter plot of the outcome measure against the imputed data
            #color the columns by whether they were imputed or not
            fig, ax = plt.subplots()
            ax.scatter(analysis_data_imputed[graph_against_col],analysis_data_imputed[col],c=imputed_datapoint)
            ax.set_xlabel(graph_against_col)
            ax.set_ylabel(col)
            ax.set_title('Imputed ' + col + ' vs outcome')
            plt.show()







    return(analysis_data_imputed)



