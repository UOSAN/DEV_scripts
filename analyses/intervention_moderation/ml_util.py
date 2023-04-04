from sklearn import svm, datasets
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.utils.validation import column_or_1d
from sklearn.utils import check_random_state
from sklearn.utils.multiclass import type_of_target
from sklearn.model_selection import StratifiedKFold
import numpy as np
import warnings


pipeline_estimator_name = 'estimator'
def get_estimator_with_preprocessing(estimator):
    return(Pipeline([('scaler',StandardScaler()),(pipeline_estimator_name,estimator)]))

def get_param_grid_with_preprocessing(estimator_param_grid):
    #prepend "estimator__" to each parameter name in param_grid
    return({(pipeline_estimator_name + '__'+k):v for k,v in estimator_param_grid.items()})



def apply_dev_moderation_standard_gridsearch(estimator,param_grid, X, y):
    grid_search_cv = GridSearchCV(
        estimator=get_estimator_with_preprocessing(estimator), 
        param_grid = get_param_grid_with_preprocessing(param_grid), cv=10,scoring='neg_mean_absolute_error')
    grid_search_cv.fit(X,y)
    return(grid_search_cv)

def extract_estimator_params_from_gridsearch(param_dict):
    dict_list = [{k.replace(pipeline_estimator_name + "__",""):param_dict[k]} for k in param_dict.keys() if k.startswith(pipeline_estimator_name)]
    #convert the dict_list into a dict
    return({k:v for d in dict_list for k,v in d.items()})


def calculate_outcome_changes(outcome_measures):
    outcome_measures['d_bf'] = outcome_measures.bf_2 - outcome_measures.bf_1
    outcome_measures['d_cancer_promoting_minus_preventing_FFQ'] = outcome_measures.cancer_promoting_minus_preventing_FFQ_w2 - outcome_measures.cancer_promoting_minus_preventing_FFQ_w1
    outcome_measures['d_FFQ_v2_Mean_Energy'] = outcome_measures.cancer_promoting_minus_preventing_FFQ_w2 - outcome_measures.cancer_promoting_minus_preventing_FFQ_w1
    
    return(outcome_measures)


def get_data_for_imputation(analysis_data):
    analysis_data_imputed = analysis_data.copy()
    return(analysis_data_imputed)




class IndependentVarStratifiedKFold(StratifiedKFold):
    def __init__(self, independent_vars, n_splits=5, shuffle=False, random_state=None):
        super().__init__(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
        self.independent_vars = independent_vars

    # def _iter_test_masks(self, X, y=None, groups=None):
    #     test_folds = self._make_test_folds(X, y)
    #     for i in range(self.n_splits):
    #         yield test_folds == i

    def _iter_test_indices(self, X, y, groups):
        unique_independent_vars, counts = np.unique(self.independent_vars, return_counts=True)
        for test_index in super()._iter_test_indices(X, self.independent_vars, groups):
            test_independent_vars = self.independent_vars[test_index]
            _, test_counts = np.unique(test_independent_vars, return_counts=True)
            if np.all(counts >= test_counts):
                yield test_index

    def _make_test_folds(self, X, y=None):
        rng = check_random_state(self.random_state)
        g = np.asarray(self.independent_vars)
        type_of_target_g = type_of_target(g)
        allowed_target_types = ("binary", "multiclass")
        if type_of_target_g not in allowed_target_types:
            warnings.warn(
                "Supported target types are: {}. Got {!r} instead.".format(
                    allowed_target_types, type_of_target_g
                )
            )

        g = column_or_1d(g)

        _, g_idx, g_inv = np.unique(g, return_index=True, return_inverse=True)
        # y_inv encodes y according to lexicographic order. We invert y_idx to
        # map the classes so that they are encoded by order of appearance:
        # 0 represents the first label appearing in y, 1 the second, etc.
        _, class_perm = np.unique(g_idx, return_inverse=True)
        g_encoded = class_perm[g_inv]

        n_classes = len(g_idx)
        g_counts = np.bincount(g_encoded)
        min_groups = np.min(g_counts)
        if np.all(self.n_splits > g_counts):
            raise ValueError(
                "n_splits=%d cannot be greater than the"
                " number of members in each class." % (self.n_splits)
            )
        if self.n_splits > min_groups:
            warnings.warn(
                "The least populated class in y has only %d"
                " members, which is less than n_splits=%d."
                % (min_groups, self.n_splits),
                UserWarning,
            )

        # Determine the optimal number of samples from each class in each fold,
        # using round robin over the sorted y. (This can be done direct from
        # counts, but that code is unreadable.)
        g_order = np.sort(g_encoded)
        allocation = np.asarray(
            [
                np.bincount(g_order[i :: self.n_splits], minlength=n_classes)
                for i in range(self.n_splits)
            ]
        )

        # To maintain the data order dependencies as best as possible within
        # the stratification constraint, we assign samples from each class in
        # blocks (and then mess that up when shuffle=True).
        test_folds = np.empty(len(g), dtype="i")
        for k in range(n_classes):
            # since the kth column of allocation stores the number of samples
            # of class k in each test set, this generates blocks of fold
            # indices corresponding to the allocation for class k.
            folds_for_class = np.arange(self.n_splits).repeat(allocation[:, k])
            if self.shuffle:
                rng.shuffle(folds_for_class)
            test_folds[g_encoded == k] = folds_for_class
        return test_folds


