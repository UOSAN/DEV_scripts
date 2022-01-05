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





#we could use these machine learning methods for outlier etection
#they seem very good but we'd have to remove NAs from the dataset
#I want to avoid that--want to just do pairwise comparisons of values that have NAs
#so I'll continue with the Carling(2000) method because it operates on one series at a time.
#https://machinelearningmastery.com/model-based-outlier-detection-and-removal-in-python/
#from sklearn.ensemble import IsolationForest

#iso = IsolationForest(contamination=0.1)
#yhat = iso.fit_predict(data_series)

#could also use 3*standard deviation from the median
#or use Spearman's correlation to reduce impact of outliers
#think about for reaction times-removing implausibly short values
#reaction times are lognormally distributed


def outlier_detection_carling(data_series_raw,show_plot=False):
    #Carling (2000) interquartile range outlier detection adjusted for n
    #https://www.sciencedirect.com/topics/mathematics/declared-outlier
    #via Rand Wilcox (2017)
    data_series_full = data_series_raw.copy()
    


    data_series_notna = data_series_full[np.isnan(data_series_full)==False]
    # Interquartile range (IQR)
    IQR = stats.iqr(data_series_notna, interpolation = 'midpoint')

    M =np.median(data_series_notna)
    n=len(data_series_notna)
    k=(17.63*n-23.64)/(7.74*n-3.71)
    kIQR = k*IQR
    
    print(M,kIQR, M-kIQR, M+kIQR)
    outlier = (data_series_notna < M-kIQR) | (data_series_notna > M+kIQR)

    outlier_indices = outlier.index[outlier]
    non_outlier_indices = outlier.index[outlier==False]

    #because of the way pandas dataseries works, we can merge this back in to the full data series and be assured that our indices will match up...
    merged_data_series = pd.merge(data_series_full,outlier,left_index=True,right_index=True,how='left')
    merged_data_series.columns = ['value','IsOutlier']
    #useful for visualization

    data_series_full.iloc[outlier_indices] = np.nan
    if show_plot:

        plt.plot(merged_data_series.iloc[non_outlier_indices].index,merged_data_series.iloc[non_outlier_indices].value,label='non-outliers',marker='.',linestyle='')
        plt.plot(merged_data_series.iloc[outlier_indices].index,merged_data_series.iloc[outlier_indices].value,label='outliers',marker='.',linestyle='')
        plt.legend()
        plt.show()
        
    return(data_series_full)


def outlier_calculation_sd(data_series_notna,sd_multiplier):
    
    # Interquartile range (IQR)
    IQR = stats.iqr(data_series_notna, interpolation = 'midpoint')

    M =np.median(data_series_notna)
    std = np.std(data_series_notna)
    n=len(data_series_notna)
    
    outlier = (data_series_notna < M-std*sd_multiplier) | (data_series_notna > M+std*sd_multiplier)
    return(outlier)

    
def outlier_detection_median_sd(data_series_raw,show_plot=False,sd_multiplier=3):
    #outliers are points 3x or more deviated from the median.
    data_series_full = data_series_raw.copy()
    


    data_series_notna = data_series_full[np.isnan(data_series_full)==False]
    
    outlier=outlier_calculation_sd(data_series_notna,sd_multiplier)
    
    outlier_indices = outlier.index[outlier]
    non_outlier_indices = outlier.index[outlier==False]

    #because of the way pandas dataseries works, we can merge this back in to the full data series and be assured that our indices will match up...
    merged_data_series = pd.merge(data_series_full,outlier,left_index=True,right_index=True,how='left')
    merged_data_series.columns = ['value','IsOutlier']
    #useful for visualization

    data_series_full.iloc[outlier_indices] = np.nan
    if show_plot:

        plt.plot(
            merged_data_series.iloc[non_outlier_indices].index, merged_data_series.iloc[non_outlier_indices].value, 
            label='non-outliers',marker='.',linestyle='')
        plt.plot(
       merged_data_series.iloc[outlier_indices].index, merged_data_series.iloc[outlier_indices].value, label='outliers',marker='.',linestyle='')
        #plt.axhline(y=)
        plt.legend()
        plt.show()
        
    return(data_series_full)



def repeated_outlier_removal(data,method,show_plot):
    data_to_process = data.copy()
    new_size=np.sum(np.isnan(data_to_process)==False)
    prev_size=new_size+1
    while new_size < prev_size:
        prev_size = new_size
        data_to_process = method(data_to_process,show_plot=show_plot)
        new_size = np.sum(np.isnan(data_to_process)==False)
        print(str(prev_size) + " , " + str(new_size))

    return(data_to_process)

def remove_selected_outliers_rtfs_study(ind_div_combined,show_plot=False):
    selected_columns =['pes_mean_limited', 'PostErrorSlowW1','IPAQ_MET_kCal','PC_trials_PostError_similarity',
                        'PE_trials_PostError_similarity','PC_trials_PostCorrect_similarity',
                        'PE_trials_PostCorrect_similarity']
    
    ind_div_combined = remove_selected_outliers(ind_div_combined,selected_columns,show_plot)
    
    return(ind_div_combined)
    
def remove_selected_outliers(ind_div_combined,outliers_to_remove,show_plot=False):
    
    for cname in outliers_to_remove:
        display(Markdown("#### " + cname))
        display(HTML('carling'))
        carling = outlier_detection_carling(ind_div_combined[cname],show_plot=show_plot)
        display(HTML('3sd'))
        sd_3 = outlier_detection_median_sd(ind_div_combined[cname],show_plot=show_plot)
        
        display(HTML('carling iterative'))
        carling_iterative = repeated_outlier_removal(ind_div_combined[cname],outlier_detection_carling,show_plot)
        
        display(HTML('3sd iterative'))
        sd_3_iterative = repeated_outlier_removal(ind_div_combined[cname],outlier_detection_median_sd,show_plot)
        
        ind_div_combined[cname] = sd_3_iterative
    
    return(ind_div_combined)






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

    individual_differences = pd.read_csv(ml_data_folderpath + "/"+ data_by_ppt_name)
    individual_differences = individual_differences.rename(columns={'SID':'subject'})
    individual_differences['wave']=1
    #individual_differences['wave'] = individual_differences['wave'].astype(object) # for compatibility with the wave column in the dataset

    individual_differences = pd.merge(individual_differences,pes_data,how='outer',left_on='subject',right_on='subid')
    individual_differences = pd.merge(individual_differences,pepc_contrast_data,how='outer',left_on='subject',right_on='subid')

    subject_pc_neural_performance = bd.X.loc[bd.X.condition_label=='CorrectGoFollowingCorrectStop',['subject','PostError_similarity','PostCorrect_similarity']]
    subject_pe_neural_performance = bd.X.loc[bd.X.condition_label=='CorrectGoFollowingFailedStop',['subject','PostError_similarity','PostCorrect_similarity']]

    subject_pc_neural_performance.columns = ['PC_trials_' + col for col in subject_pc_neural_performance.columns]
    subject_pe_neural_performance.columns = ['PE_trials_' + col for col in subject_pe_neural_performance.columns]
    subject_neural_performance = subject_pc_neural_performance.merge(subject_pe_neural_performance,left_on='PC_trials_subject',right_on='PE_trials_subject',how='outer')
    subject_neural_performance =subject_neural_performance.rename(columns = {'PC_trials_subject':'subject'})

    ind_div_combined = subject_neural_performance.merge(individual_differences,left_on='subject',right_on='subject',how='left')
    
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


def visualize_corr(neural_var,correlate,data):
    display(HTML(correlate))
    #nan_rows = np.isnan(data[correlate])
    nan_rows = np.isnan(data[correlate]) | np.isnan(data[neural_var])
    cor2way_df = data.loc[nan_rows==False,]
    pearson_result = pearsonr(cor2way_df[neural_var],cor2way_df[correlate])
    display(HTML("r=" + format(pearson_result[0],".2f") +"; p-value=" + format(pearson_result[1],".4f")))
    spearman_result = spearmanr(cor2way_df[neural_var],cor2way_df[correlate])
    display(HTML("rho=" + format(spearman_result[0],".2f") +"; p-value=" + format(spearman_result[1],".4f")))
    cplot = pyplot.scatter(cor2way_df[neural_var],cor2way_df[correlate])
    cplot.axes.set_xlabel(neural_var)
    cplot.axes.set_ylabel(correlate)
    pyplot.show()