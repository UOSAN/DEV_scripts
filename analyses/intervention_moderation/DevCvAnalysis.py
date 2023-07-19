import pandas as pd
from dev_interaction_util import *
from typing import Callable, Union


class DevCvAnalysis:
    ###
    # This class is for encapsulating a single cross-validation analysis of the DEV data


    def __init__(self, dropbox_data_dir):
        self.dropbox_data_dir = dropbox_data_dir
        self.data_by_ppt_path = dropbox_data_dir + '/data_by_ppt.csv'
        self.data_by_wave_ppt_path = dropbox_data_dir + '/data_by_wave_ppt.csv'
        self.group_codes_path = dropbox_data_dir + '/DEV-GroupAbridged_DATA_LABELS_2023-06-23_1859.csv'
        self.data_codebook_path = dropbox_data_dir + 'data_codebook_DEV - data_codebook_optimized.csv'
        self.mastersheet_path = dropbox_data_dir + 'DEV Participant Mastersheet_copy.xlsx'

        self.run_real_analysis=False

        self.analysis_data = None
        
        self.outcome_measures = None
        self.__predictor_data = None
        self.__predictors_main_names = []
        self.__predictors_interactions_names = []
        self.__full_dataset = None
        #self.__predictors_groups = []
        self.group_assignment_onehots = None
        self.outcome = None
        self.predictor_subset = None


    def set_predictor_subset(self, predictor_subset: list):
        '''
        sets a record of the predictors to be used for the analysis
        allows some predictors to be excluded from the analysis
        '''
        #ensure that all the predictros in the subset exist
        for p in predictor_subset:
            if p not in self.__predictor_data.columns:
                raise ValueError("predictor " + p + " not found in the predictor data")
            
        self.predictor_subset = predictor_subset


    def get_full_dataset(self):
        return(self.__full_dataset)

    def get_predictor_data(self):
        return(self.__predictor_data)
    
    '''
    Gets predictors excluding interaction terms and groups
    '''
    def get_main_predictor_data(self):
        return(self.__predictor_data[self.__predictors_main_names])

    def get_interaction_predictor_data(self):
        return(self.__predictor_data[self.__predictors_interactions_names])

    def get_active_predictor_subset(self) -> pd.DataFrame:
        return(self.__predictor_data[self.predictor_subset])
    
    '''
    set_predictor_data:
    currently deprecated and will throw an error
    let's make this immutable for now!
    '''
    def set_predictor_data(self, predictor_data):
        raise NotImplementedError("currently predictor data is immutable once it has been set")
        self.__predictor_data = predictor_data
        self.__predictors_main_names = predictor_data.columns




    def get_predictors_main_names(self):
        return(self.__predictors_main_names)
    
    def get_predictors_interaction_names(self):
        return(self.__predictors_interactions_names)
    

    


    def load_and_preprocess_data_full(self, 
        use_dummy_outcome_data=True,
        include_neural_data=False,
        include_groups=False,
        rearrange_groups=None,
        predictor_transform_func=None,
        groups_to_remove = []
        ):
        """
        
        Load the data and preprocess it
        does not include imputing data
        does include getting outcome and group assignment data

        Parameters:
        rearrange_groups (dict): if not None, then a dictionary mapping group names to new group names

        Returns:
        bool: Description of return value

        """


        data_by_ppt = pd.read_csv(self.data_by_ppt_path)
        data_codebook = pd.read_csv(self.data_codebook_path,skiprows=1)
        if include_groups:
            group_codes = load_groups_from_mastersheet(self.mastersheet_path)

            if self.run_real_analysis==False:
                group_codes['intervention_group'] = group_codes['intervention_group'].sample(frac=1,random_state =43 ,replace=False)#.reset_index(drop=True)

            #now merge the group codes with the data_by_ppt
            #get participants in the data_by_ppt before merging group_codes
            pre_group_merge_participants = data_by_ppt.SID.unique()

            data_by_ppt = data_by_ppt.merge(group_codes, how='inner', left_on='SID', right_on='dev_id')
            post_group_merge_participants = data_by_ppt.SID.unique()
            if len(pre_group_merge_participants) != len(post_group_merge_participants):
                print("WARNING: merging group codes with data_by_ppt resulted in a different number of participants")
                print("pre merge: " + str(len(pre_group_merge_participants)))
                print("post merge: " + str(len(post_group_merge_participants)))
                print("participants in pre merge but not post merge: " + str(set(pre_group_merge_participants).difference(set(post_group_merge_participants))))

            if rearrange_groups is not None:
                data_by_ppt['intervention_group'] = data_by_ppt['intervention_group'].map(rearrange_groups)


        #find out which columns in data_by_ppt are missing from the codebook
        data_by_ppt.columns.difference(data_codebook['VarName'])


        if include_neural_data:
            roi_data = load_roi_data(self.dropbox_data_dir)
            raw_predictors = data_by_ppt.merge(roi_data, how='outer', left_on='SID', right_on = 'subject_id')
        else:
            raw_predictors = data_by_ppt
        del data_by_ppt

        raw_predictors.sort_values(by=['SID'],inplace=True)


        if use_dummy_outcome_data:
            #copy our outcome measures, bf_1 and FFQ_1, into a new dataframe
            raw_predictors['bf_2'] = raw_predictors.bf_1
            #need to decide what sort of FFQ we want to use
            raw_predictors['cancer_promoting_minus_preventing_FFQ_1'] = raw_predictors.cancer_promoting_minus_preventing_FFQ
            raw_predictors['cancer_promoting_minus_preventing_FFQ_2'] = raw_predictors.cancer_promoting_minus_preventing_FFQ
            outcomes_s2_minus_s1 = raw_predictors.loc[:,data_codebook.loc[data_codebook.IsSelectedDraftOutcomeMeasure,"VarName"]].copy()
            raise Exception("this is broken; these aren't _really_ the difference scores, and if you're using dummy you need to figure this out later on in the code.")
        else:
            
            outcomes_s2_minus_s1 = get_outcome_diff_scores_from_longitudinal(self.data_codebook_path,self.data_by_wave_ppt_path)
            outcome_cols_only = outcomes_s2_minus_s1.columns
            #OK, now we need to make sure that we have the same set of subjects in the outcome_measures_long and data_by_ppt
            #get the set of subjects in each
            subjects_in_outcomes = set(outcomes_s2_minus_s1.SID)
            subjects_in_raw_predictors = set(raw_predictors.SID)
            #get the intersection of these two sets
            subjects_in_both = list(subjects_in_outcomes.intersection(subjects_in_raw_predictors))
            subjects_in_both.sort()
            #now turn that into a one-column dataframe, and left-join each independently on that dataframe
            subjects_in_both_df = pd.DataFrame({'SID':subjects_in_both})

            outcomes_s2_minus_s1 = subjects_in_both_df.merge(outcomes_s2_minus_s1, how='left', on='SID')
            
            raw_predictors = subjects_in_both_df.merge(raw_predictors, how='left', on='SID')

            #if groups are marked for removal, remove them
            #test if each element in the series raw_predictors.intervention_group is in groups_to_remove
            #if it is, then set it to np.nan
            rows_to_remove = raw_predictors.intervention_group.isin(groups_to_remove)
            raw_predictors = raw_predictors.loc[rows_to_remove==False,:].reset_index(drop=True)
            outcomes_s2_minus_s1 = outcomes_s2_minus_s1.loc[rows_to_remove==False,:].reset_index(drop=True)
            

            outcomes_s2_minus_s1 = outcomes_s2_minus_s1.loc[:,outcome_cols_only].copy()

        if predictor_transform_func is not None:
            raw_predictors = predictor_transform_func(raw_predictors)

        # do a report on missing data
        predictors_df  = raw_predictors.loc[:,data_codebook.loc[data_codebook.Aim3PredictorsFinal,"VarName"]].copy()

        na_values = pd.DataFrame(raw_predictors.isna().sum())
        na_values.columns = ['NA_Count']
        na_values['prop_NA'] = na_values.NA_Count / raw_predictors.shape[0]
        data_codebook = data_codebook.merge(na_values, left_on='VarName', right_index=True)

        data_codebook.to_csv(self.dropbox_data_dir + 'data_metadata.csv', index=False)

        one_hot_vals = pd.get_dummies(predictors_df.birthsex_factor)
        #there's only two variables here so we can convert this into a dummy variable
        predictors_df.drop(columns=['birthsex_factor'], inplace=True)
        one_hot_vals.columns = ['birthsex_factor_' + str(col) for col in one_hot_vals.columns]
        predictors_df = predictors_df.join(one_hot_vals.iloc[:,1:])

        if self.run_real_analysis==False:
            #randomize the outcomes, but keep the SIDs the same. 
            # #the point is to randomize the allocation of outcomes to subjects in order to get random data
            #not to just shuffle the order of the rows.
            outcomes_sid = outcomes_s2_minus_s1.SID.tolist()
            outcomes_s2_minus_s1 = outcomes_s2_minus_s1.sample(frac=1, random_state=42).reset_index(drop=True)
            outcomes_s2_minus_s1['SID'] = outcomes_sid
            print("run_real_analysis is False, so we're randomizing the outcomes, but keeping the SIDs the same. ")
        else:
            print("run_real_analysis is True, so we're not randomizing the outcomes. ")

        self.__predictor_data=predictors_df.copy()
        self.__predictors_main_names=predictors_df.columns.tolist()
        self.__full_dataset = raw_predictors.copy()

        self.outcome_measures=outcomes_s2_minus_s1.copy()

        self.group_assignments=raw_predictors.loc[:,'intervention_group'].copy()

        
        return(predictors_df, outcomes_s2_minus_s1,self.group_assignments)
    
    def set_outcome_target(self, outcome_target_name):
        '''
        This function sets the outcome target for the analysis to a single specific outcome measure.
        It will also remove rows where there is not data for that target
        '''
        self.outcome = self.outcome_measures[outcome_target_name]
        outcome_is_na = self.outcome.isna()
        self.outcome = self.outcome[~outcome_is_na]
        self.__predictor_data = self.__predictor_data[~outcome_is_na]
        self.group_assignments = self.group_assignments[~outcome_is_na]
        self.group_assignment_onehots = self.group_assignment_onehots[~outcome_is_na]
        

    
    def set_up_interactions_and_groups(self, reference_group):
        group_assignments = self.group_assignments
        
        pd_main = self.__predictor_data[self.__predictors_main_names].copy()
        predictor_data, group_assignment_onehots = set_up_interactions_from_group_assignments(pd_main, group_assignments,reference_group)
        self.__predictor_data = predictor_data
        #interaction names are the new names in predictor_data but not pd_main
        self.__predictors_interactions_names = [col for col in predictor_data.columns if col not in pd_main.columns]
        self.group_assignment_onehots = group_assignment_onehots



    #Need to add imputation in the dataset below!
    # First, we set up a function that loops runs the scoring loop do_scoring_loop (which does one cross-validation analysis), and then additionally:
    # - selects the best model based on the overall results
    # - Runs a final fit
    # - presents model results
    def score_and_present(self,
                        predictor_data,
                        outcome_measure,
                        group_assignments,
                        #hyper_selection_function : Union[Callable, str] ='main'
                        hyper_selection_function=None
                        ):
        if hyper_selection_function is None:
            hyper_selection_function=do_hyperparameter_selection_loop
        
        # if hyper_selection_function=='fast':
        #     hyper_selection_function=do_hyperparameter_selection_loop_fast
        # elif hyper_selection_function=='main':
        #     hyper_selection_function=do_hyperparameter_selection_loop



        # predictor_data = self.__predictor_data
        # outcome_measure = self.outcome
        # group_assignments = self.group_assignment_onehots
        scoring_data = do_scoring_loop(X=predictor_data, y= outcome_measure, 
                    groups = group_assignments, 
                    hyperparameter_selection_on_fold=hyper_selection_function,
                    outer_folds=5)

        scores = scoring_data['scores']
        best_models = scoring_data['best_models']
        best_params_df_list = scoring_data['best_params_df_list']
        raw_cv_results_list = scoring_data['raw_cv_results_list']

        print("scores:")
        print(scores)
        overall_score = np.mean(scores)
        print("overall_score:")
        print(overall_score)


        
        best_model = get_best_model(summarize_overall_df_results(raw_cv_results_list))
        final_fit = do_final_fit(X=predictor_data, y= outcome_measure, final_model=best_model, impute_missing=True)

        pd_imputed, X_was_imputed = apply_imputer(predictor_data)

        final_results = present_model_results(X=pd_imputed, final_fit=final_fit, y=outcome_measure)

        #print rows of final_results where feature_name is the list of features to check
        # if interaction_effect_df is not None:
        #     base_regressors = interaction_effect_df.predictor[interaction_effect_df.interaction_effect!=0]
        #     regressors_to_check = [x+y for y in ['','*ni','*san'] for x in base_regressors]
        #     final_results['planned_regression'] = final_results['predictor'].isin(regressors_to_check)
        

        #this is only for synethetic analysis
        #present_results_vs_ground_truth_cors(pd_imputed,outcome_measure,group_assignments,final_results,base_regressors)

        return({
            'final_results':final_results,
            'final_fit':final_fit,
            'overall_score':overall_score
            })


    