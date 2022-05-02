from nilearn import plotting
from nilearn.image import smooth_img, binarize_img
from nilearn.masking import compute_brain_mask, unmask, apply_mask
from matplotlib import pyplot
from scipy.stats import pearsonr, spearmanr
import pickle
from IPython.core.display import display, HTML, Markdown
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import sklearn.svm


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
    
def visualize_series_corr(series1,series2):
    display(HTML(series1.name))
    pearson_result = pearsonr(series1,series2)
    display(HTML("r=" + format(pearson_result[0],".2f") +"; p-value=" + format(pearson_result[1],".4f")))
    spearman_result = spearmanr(series1,series2)
    display(HTML("rho=" + format(spearman_result[0],".2f") +"; p-value=" + format(spearman_result[1],".4f")))
    cplot = pyplot.scatter(series1,series2)
    cplot.axes.set_xlabel(series1.name)
    cplot.axes.set_ylabel(series2.name)
    pyplot.show()
    
    
#developed in poster-presentation-visualization_test
#arguably not a "visualization"; however the primary purpose of this is for visualiztion
#so I think it is more or less suitable
def get_LinearSVC_coefs(classifier_object, mask_nifti, smoothing=None):
    assert(str(type(classifier_object))=="<class 'sklearn.svm._classes.LinearSVC'>")
    
    features_raw = classifier_object.coef_
    
    features_initial = unmask(features_raw, mask_nifti)
    
    #we're going to apply smoothing. we need to smooth mask and the original image
    if smoothing is None:
        features_nifti = features_initial
    else:
        #smooth the mask
        smoothed_mask = smooth_img(mask_nifti,smoothing)

        #now we wanna threshold that mask to only include items of the mask that are actually part of it.
        mask_value=np.max(mask_nifti.get_fdata())
        smoothed_mask_bin = binarize_img(smoothed_mask, mask_value*0.99)
        
        #now apply the ORIGINAL UNSMOOTHED mask
        features_smoothed = smooth_img(features_initial,smoothing)
        #then mask it according to the smoothed mask
        features_nifti = unmask(
            apply_mask(features_smoothed,smoothed_mask_bin),
            smoothed_mask_bin
            )
        
    return(features_nifti)
        
# features_nifti_sm1 = get_LinearSVC_coefs(forced_choice_results['classifier'],
#                    Brain_Data_allsubs.a['mask_nifti'].value,
#                    2)