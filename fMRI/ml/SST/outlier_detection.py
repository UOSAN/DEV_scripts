from nilearn import surface
from nilearn import datasets
from nilearn import plotting
from matplotlib import pyplot
from scipy.stats import pearsonr, spearmanr
import pickle
from IPython.core.display import display, HTML, Markdown
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
    
    if show_plot: print(M,kIQR, M-kIQR, M+kIQR)
    outlier = (data_series_notna < M-kIQR) | (data_series_notna > M+kIQR)

    outlier_indices = outlier.index[outlier]
    non_outlier_indices = outlier.index[outlier==False]

    #because of the way pandas dataseries works, we can merge this back in to the full data series and be assured that our indices will match up...
    merged_data_series = pd.merge(data_series_full,outlier,left_index=True,right_index=True,how='left')
    merged_data_series.columns = ['value','IsOutlier']
    #useful for visualization

    data_series_full.iloc[outlier_indices] = np.nan
    if show_plot:

        plt.plot(
            merged_data_series.iloc[non_outlier_indices].index,merged_data_series.iloc[non_outlier_indices].value,
            label='non-outliers',marker='.',linestyle='')
        
        plt.plot(merged_data_series.iloc[outlier_indices].index, 
                     merged_data_series.iloc[outlier_indices].value, label='outliers', marker='.', linestyle='')
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
        print(data_series_raw.name)
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
    
    #a fix if the datatype is type object
    if str(data_to_process.dtype)=="object":
        series_modal_data_type = pd.Series([type(x) for x in data_to_process]).mode()[0] #get it
        #make it the type of its modal type.
        data_to_process = data_to_process.astype(float)

    new_size=np.sum(np.isnan(data_to_process)==False)
    prev_size=new_size+1
    while new_size < prev_size:
        prev_size = new_size
        data_to_process = method(data_to_process,show_plot=show_plot)

        new_size = np.sum(np.isnan(data_to_process)==False)
        if show_plot: print(str(prev_size) + " , " + str(new_size))

    return(data_to_process)

def remove_selected_outliers_rtfs_study(ind_div_combined,show_plot=False):
    selected_columns =['pes_mean_limited', 'PostErrorSlowW1','IPAQ_MET_kCal','PC_trials_PostError_similarity',
                        'PE_trials_PostError_similarity','PC_trials_PostCorrect_similarity',
                        'PE_trials_PostCorrect_similarity']
    
    ind_div_combined = remove_selected_outliers(ind_div_combined,selected_columns,show_plot)
    
    return(ind_div_combined)
    
def remove_selected_outliers_range(ind_div_combined,outliers_to_remove,show_plot=False):
    
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

def remove_selected_outliers(ind_div_combined,outliers_to_remove,show_plot=False):
    
    for cname in outliers_to_remove:
        sd_3_iterative = repeated_outlier_removal(ind_div_combined[cname],outlier_detection_median_sd,show_plot)
        
        ind_div_combined[cname] = sd_3_iterative
    
    return(ind_div_combined)

