from dev_interaction_util import *
from logging import warning
from DevCvAnalysis import DevCvAnalysis
from IPython.display import display, Markdown


class InterventionCVManager:




    def __init__(self, dropbox_data_dir):
        self.dropbox_data_dir = dropbox_data_dir
        self.mode='pipeline_test'
        self.group_mode = 'default'
        self.custom_codebook_path = None
        self.custom_outcomes_path = None


    


    def get_prepopulated_dev_cv_analysis(self,set_as_random=True):

        dev_cv_analysis = DevCvAnalysis(self.dropbox_data_dir)

        if self.custom_outcomes_path is not None:
            dev_cv_analysis.data_by_wave_ppt_path = self.custom_outcomes_path

        if self.custom_codebook_path is not None:
            dev_cv_analysis.data_codebook_path = self.custom_codebook_path
        ## scramble groups and 
        dev_cv_analysis.run_real_analysis = set_as_random==False

        groups_to_remove = []
        if self.group_mode=='default':
            groups_rekey = None
            reference_group = 'willamette'
        elif self.group_mode=='dichotomous':
            groups_rekey = {
                'willamette': 'control',
                'mckenzie': 'intervention',
                'umpqua': 'intervention'
            }
            reference_group = 'control'
        elif self.group_mode=='exclude_mckenzie':
            groups_rekey = None
            reference_group = 'willamette'
            groups_to_remove=['mckenzie']

        analysis_data, outcome_measures_raw,group_assignments = dev_cv_analysis.load_and_preprocess_data_full(
            use_dummy_outcome_data=False,
            include_neural_data=True, include_groups=True,
            rearrange_groups=groups_rekey,
            predictor_transform_func = get_combined_roi_analyses,
            groups_to_remove=groups_to_remove
            )
        


        dev_cv_analysis.set_up_interactions_and_groups(reference_group = reference_group)


        return(dev_cv_analysis)

    def do_predictor_set_comparison_with_preloaded_dev_cv(self, predictor_sets, outcome_var, devCVAnalysis: DevCvAnalysis):
        raise NotImplementedError()
    


    def do_predictor_set_comparison(self, predictor_sets, outcome_var, mode='full_pipeline_test'):
        model_outcomes = {}
        for psk in predictor_sets.keys():
            # print markdown header for this set
            display(Markdown('## ' + psk))


            predictor_set = predictor_sets[psk]
            print("loading raw data")
            if self.mode=='fast_pipeline_test':
                devCVAnalysis = self.get_prepopulated_dev_cv_analysis(set_as_random=True)
                hyper_func = do_hyperparameter_selection_loop_fast
            elif self.mode=='full_pipeline_test':
                devCVAnalysis = self.get_prepopulated_dev_cv_analysis(set_as_random=True)
                hyper_func = do_hyperparameter_selection_loop
            elif self.mode=='fast_analysis':
                devCVAnalysis = self.get_prepopulated_dev_cv_analysis(set_as_random=False)
                hyper_func = do_hyperparameter_selection_loop_fast
            elif self.mode=='full_analysis':
                devCVAnalysis = self.get_prepopulated_dev_cv_analysis(set_as_random=False)
                hyper_func = do_hyperparameter_selection_loop

            devCVAnalysis.set_outcome_target(outcome_var)

            devCVAnalysis.set_predictor_subset(predictor_set)


            
            
            
            
            print(" attempting to predict " + outcome_var + " with " + str(len(predictor_set)) + " predictors in the set " + psk)
            print('predictors in that set are ' + " ".join(predictor_set))
            model_outcomes[psk] = devCVAnalysis.score_and_present(
                devCVAnalysis.get_active_predictor_subset(),
                devCVAnalysis.outcome,
                devCVAnalysis.group_assignments,
                hyper_selection_function=hyper_func
                    )
            
        #get a dictionary of the overall scores for each model
        model_outcomes_comparison = { k:
            model_outcomes[k]['overall_score'] for k in model_outcomes.keys()}

        print(model_outcomes_comparison)
            
        return(model_outcomes)
