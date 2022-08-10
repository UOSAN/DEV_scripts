from nltools import Brain_Data
from scipy.stats import ttest_ind
from nltools import expand_mask
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath("../../ml/"))

from apply_loocv_and_save import *
import gc
import nibabel as nib

nonbids_data_path = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/"
ml_data_folderpath = "/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/ml"
train_test_markers_filepath = ml_data_folderpath + "/train_test_markers_20210601T183243.csv"

all_sst_events= pd.read_csv(ml_data_folderpath +"/SST/" + "all_sst_events.csv")

script_path = '/gpfs/projects/sanlab/shared/DEV/DEV_scripts/fMRI/ml'


brain_data_filepath = ml_data_folderpath + "/SST/Brain_Data_betaseries_40subs_correct_cond.pkl"
bd=pickle.load(open(brain_data_filepath,'rb'))
bd.X

test_train_set = pd.read_csv(train_test_markers_filepath)

with open(brain_data_filepath, 'rb') as pkl_file:
    Brain_Data_allsubs = pickle.load(pkl_file)

dev_wtp_io_utils.check_BD_against_test_train_set(Brain_Data_allsubs,test_train_set) #ensure there's no test subjects in this dataset
#need to clean the dataset before running similarity. not sure at what point we do this.
#first_subs_nifti = nil.image.clean_img(first_subs_nifti,detrend=False,standardize=True)
#time is along first axis
#https://github.com/nilearn/nilearn/blob/1607b52458c28953a87bbe6f42448b7b4e30a72f/nilearn/signal.py#L27
#nifti standardize gets the mean and std on axis zero (time axis) and standardizes
#brain_data standardize does the same https://nltools.org/_modules/nltools/data/brain_data.html#Brain_Data.standardize
#so we can replace nifti standardize with brain_data

#bd_std = bd.standardize(method="zscore")
bd_std = bd

def get_interclass_correlation(bd_subj_i,mask_b = None):
    if mask_b is None:
        similarity_matrix = bd_subj_i.distance(metric='correlation').distance_to_similarity()
    else:
        similarity_matrix = bd_subj_i.apply_mask(mask_b).distance(metric='correlation').distance_to_similarity()
    print(".",end="")
    similarity_matrix.labels=bd_subj_i.X.trial_type.tolist()
    
        #now we get average interclass correlation
    similarity_matrix_arr = similarity_matrix.squareform()

    print(".",end="")
    #create dataframe to put it in
    mat_length = similarity_matrix.square_shape()[0]
    combo_count = int(mat_length*(mat_length-1)/2)
    paired_list = pd.DataFrame({
      'interclass': np.empty(combo_count,bool),
        'similarity':np.empty(combo_count,float),
        'class_combo':np.empty(combo_count,str)

    })
    ij=0
    for i in range(0,mat_length):
        for j in range(i+1,mat_length):
            interclass_i_j = similarity_matrix.labels[i]==similarity_matrix.labels[j]
            paired_list.loc[ij,'interclass']=interclass_i_j
            paired_list.loc[ij,'similarity']=similarity_matrix_arr[i,j]
            #create a label for this type of combination that is order-invariant
            if interclass_i_j:
                class_combo = similarity_matrix.labels[i]
            else:
                class_member_types = [similarity_matrix.labels[i],similarity_matrix.labels[j]]
                class_member_types.sort()
                class_combo = ", ".join(class_member_types)
            paired_list.loc[ij,'class_combo']=class_combo
            ij+=1
            
    print(".",end="",flush=True)
    
    return(paired_list)


mask = Brain_Data(ml_data_folderpath + "/Neurosynth Parcellation_0.nii.gz")
mask_names = pd.read_csv(ml_data_folderpath + "/parcellation_0_labels.csv")
mask_ex = expand_mask(mask)

mask_ex.X = mask_names

#from IPython.display import display


correlations_by_mask = {}
#loop through masks
for mask_i in mask_ex:
    mask_name = mask_i.X[1]
    print(mask_name)
    mask_results_list = []
    #loop through subjects
    for subj_i in np.unique(bd_std.X.subject):
        print(subj_i,end=", ")
        
        #extract the data for this specific subject from the brain data
        subj_i_betas = bd_std.X.subject==subj_i
        bd_subj_i = bd_std[subj_i_betas,]

        #make sure we have enough data to analyze
        unique_trial_types = len(np.unique(bd_std.X.trial_type))
        if unique_trial_types<2:
            print("only one trial type for " + subj_i + "; skipping.")
            continue
            
        #get the interclass correlations. this does a LOT of work.
        paired_list = get_interclass_correlation(bd_subj_i,mask_i)
        l=paired_list

        #do statistical analysis on the results for this mask and subect
        ttest_res = ttest_ind(l[l.interclass==True].similarity,l[l.interclass==False].similarity)
        combined_result_df = np.transpose(pd.DataFrame(l.groupby('class_combo').similarity.mean()))
        combined_result_df['statistic'] = ttest_res.statistic
        combined_result_df['pvalue'] = ttest_res.pvalue
        
        mask_results_list = mask_results_list + [combined_result_df]
        
    mask_results_df = pd.concat(mask_results_list)
    print(mask_results_df)
    

    
    correlations_by_mask[mask_name] = mask_results_df
    
    
with open(ml_data_folderpath + "/SST/correlations_40_no_std.pkl", 'wb') as pkl_file:
    pickle.dump(correlations_by_mask,file=pkl_file)