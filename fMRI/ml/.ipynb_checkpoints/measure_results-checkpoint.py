import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from scipy.stats import pearsonr, spearmanr
import math
import seaborn as sns
import matplotlib.pyplot as plt
import nibabel as nib
from nilearn import plotting


def pearsonr_cor_func(obs,pred):
    return(pearsonr(obs,pred)[0])

def spearmanr_cor_func(obs,pred):
    return(spearmanr(obs,pred)[0])

    
def within_group_performance(results,cor_func,
                             group_col_name='result_group',
                             obs_col_name='y',
                             pred_col_name='y_pred'
                             
                            ):
    results[obs_col_name] = results[obs_col_name].astype(float)
    results[pred_col_name] = results[pred_col_name].astype(float)
    within_subj_predictions = []
    for group in results[group_col_name].unique():
        group_results = results.loc[results[group_col_name]==group,].copy()

        #get means and SDs
        obs_mean = np.mean(group_results[obs_col_name])
        pred_mean = np.mean(group_results[pred_col_name])
        obs_sd = np.std(group_results[obs_col_name])
        pred_sd = np.std(group_results[pred_col_name])

        #mean center
        group_results[obs_col_name] = (group_results[obs_col_name] - obs_mean)
        group_results[pred_col_name] = (group_results[pred_col_name] - pred_mean)

        within_subj_prediction = pearsonr(group_results[obs_col_name],group_results[pred_col_name])[0]
        #print(within_subj_prediction)
        #print(math.pow(pearsonr(group_results[obs_col_name],group_results['y_pred'])[0],2))


        #what if we we re-ranked the predicted values into groups along the 
        if (within_subj_prediction< (-0.5)):

            sp = sns.scatterplot(group_results[obs_col_name],group_results[pred_col_name])
            plt.show()
            display(pd.DataFrame(group_results.groupby(obs_col_name).y_pred.mean()))
            #display(group_results)
        within_subj_predictions = within_subj_predictions + [within_subj_prediction]
    return(within_subj_predictions)