from nilearn import surface
from nilearn import datasets
from nilearn import plotting
from matplotlib import pyplot
from scipy.stats import pearsonr, spearmanr
import pickle
from IPython.core.display import display, HTML, Markdown
from nilearn import plotting
from nilearn.masking import compute_brain_mask
import nltools as nlt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from outlier_detection import *




def plot_stat_maps(ns1,ns2):
    plotting.plot_stat_map(ns1, display_mode='z',
                           cut_coords=range(20, 61, 10), title='Slices',cmap='RdBu')

    plotting.plot_stat_map(ns2, display_mode='z',
                           cut_coords=range(20, 61, 10), title='Slices',cmap='RdBu')
    pyplot.show()


def get_bd(brain_data_filepath,ns1,ns2,relevant_mask,condition1_name = 'PostError_similarity',condition2_name = 'PostCorrect_similarity',similarity_method='correlation'):
    bd=pickle.load(open(brain_data_filepath,'rb'))
    
    if relevant_mask is None:
        relevant_mask = nlt.Brain_Data(ns1).mask
    print("applying mask")
    bd_to_measure = bd.apply_mask(relevant_mask)
    #bd_PostError=bd[bd.X.condition_label=="CorrectGoFollowingFailedStop"]

    #bd.X.condition_label.value_counts()

    print("getting similarity 1")
    #bd.X[condition1_name] = (bd_to_measure.similarity(ns1))
    bd.X[condition1_name] = (nlt.Brain_Data(ns1).similarity(bd_to_measure,similarity_method))
    print("getting similarity 2")
    #bd.X[condition2_name] = (bd_to_measure.similarity(ns2))
    bd.X[condition2_name] = (nlt.Brain_Data(ns2).similarity(bd_to_measure,similarity_method))

    return(bd)

def create_histogram(
    bd,
    similarity1 = 'PostError_similarity',
    similarity2 = 'PostCorrect_similarity', 
    condition1 = 'CorrectGoFollowingFailedStop',
    condition2 = 'CorrectGoFollowingCorrectStop'):
    print("creating histograms")
    bd_to_plot = bd.X[['condition_label',similarity1,'subject']].pivot(index='subject',columns='condition_label',values=similarity1).reset_index()

    quantiles = bd.X[[similarity1]].quantile([0.1,0.9]).iloc[:,0].values.tolist()
    quantile_range = quantiles[1]-quantiles[0]
    plot_range = [quantiles[0] - quantile_range*0.5,quantiles[1] + quantile_range*0.5] 
    bins = np.linspace(plot_range[0],plot_range[1],50)

    
    pyplot.hist(
        bd_to_plot[[condition1,condition2]]#.to_numpy()
        ,bins=bins
        ,alpha=0.5,histtype='stepfilled',label=[condition1,condition2])
    pyplot.legend(prop={'size': 10})
    pyplot.show();


    display(HTML(pd.DataFrame(bd.X.groupby('condition_label').agg({
        similarity1:"mean",
        similarity2:"mean"})).to_html()))
    

data_by_ppt_name = "data_by_ppt_2021_12_29.csv"

def get_ind_div_for_pes_combined(bd,ml_data_folderpath):

    pes_data = pd.read_csv(ml_data_folderpath + "/post_error_slowing.csv",index_col=0)
    pepc_contrast_data = pd.read_csv(ml_data_folderpath + "/post_error_slowing_simple_approach.csv",index_col=0)
    print(pes_data.columns)
    print(pepc_contrast_data.columns)

    individual_differences = pd.read_csv(ml_data_folderpath + "/"+ data_by_ppt_name)
    individual_differences = individual_differences.rename(columns={'SID':'subject'})
    individual_differences['wave']=1
    #individual_differences['wave'] = individual_differences['wave'].astype(object) # for compatibility with the wave column in the dataset

    individual_differences = pd.merge(individual_differences,pes_data,how='outer',left_on='subject',right_on='subid')
    individual_differences = pd.merge(individual_differences,pepc_contrast_data,how='outer',left_on='subject',right_on='subid')
    
    if (type(bd)==pd.DataFrame):
        bd = bd.rename(columns={'subid':'subject'})
        ind_div_combined = bd.merge(individual_differences,left_on='subject',right_on='subject',how='left')
    else:
        #brain data is unprocessed; process it
        subject_pc_neural_performance = bd.X.loc[bd.X.condition_label=='CorrectGoFollowingCorrectStop',['subject','PostError_similarity','PostCorrect_similarity']]
        subject_pe_neural_performance = bd.X.loc[bd.X.condition_label=='CorrectGoFollowingFailedStop',['subject','PostError_similarity','PostCorrect_similarity']]

        subject_pc_neural_performance.columns = ['PC_trials_' + col for col in subject_pc_neural_performance.columns]
        subject_pe_neural_performance.columns = ['PE_trials_' + col for col in subject_pe_neural_performance.columns]
        subject_neural_performance = subject_pc_neural_performance.merge(subject_pe_neural_performance,left_on='PC_trials_subject',right_on='PE_trials_subject',how='outer')
        subject_neural_performance =subject_neural_performance.rename(columns = {'PC_trials_subject':'subject'})

        ind_div_combined = subject_neural_performance.merge(
            individual_differences,left_on='subject',right_on='subject',how='left')
    
    #remove outliers
    
    return(ind_div_combined)



def get_ind_div_for_sst(bd, ml_data_folderpath):
    individual_differences = pd.read_csv(ml_data_folderpath + "/" + data_by_ppt_name)
    individual_differences = individual_differences.rename(columns={'SID':'subject'})
    individual_differences['wave']=1
    #individual_differences['wave'] = individual_differences['wave'].astype(object) # for compatibility with the wave column in the dataset
    
    subject_cs_neural_performance = bd.X.loc[bd.X.condition_label=='CorrectStop',['subject','CS_similarity','CG_similarity']]
    subject_cg_neural_performance = bd.X.loc[bd.X.condition_label=='CorrectGo',['subject','CS_similarity','CG_similarity']]

    subject_cs_neural_performance.columns = ['CS_trials_' + col for col in subject_cs_neural_performance.columns]
    subject_cg_neural_performance.columns = ['CG_trials_' + col for col in subject_cg_neural_performance.columns]
    subject_neural_performance = (
        subject_cs_neural_performance.merge(subject_cg_neural_performance,left_on='CS_trials_subject',right_on='CG_trials_subject',how='outer')
    )
    
    subject_neural_performance =subject_neural_performance.rename(columns = {'CS_trials_subject':'subject'})
    
    ind_div_combined = subject_neural_performance.merge(individual_differences,left_on='subject',right_on='subject',how='left')
    
    return(ind_div_combined)

from visualization import visualize_corr, visualize_series_corr