import sys
import os
sys.path.append(os.path.abspath("../../ml/"))

import pandas as pd
import scipy.io
import re
import sys
import warnings
import pickle
from mvpa2.datasets.mri import fmri_dataset, map2nifti
from mvpa2 import *
import mvpa2.datasets 
import nibabel as nib
import numpy as np
import nibabel as nib
from nilearn.image import resample_img
import nilearn

class BehavioralDataNotFoundForBrainDataException(Exception):
    """Behavioral data could not be matched to a subject."""
    pass

def sa_to_df(sa_collectable,column_filter=None):
    sa_index = pd.DataFrame({sa:sa_collectable[sa].value for sa in sa_collectable if (column_filter is None) or (sa in column_filter)})
    return(sa_index)
        
## get a list of the subject folders
## iterate through them
## pass in a design matrix appropriate for that subject (pretty much just subject ID and then name of condition)
## append

def import_beta_series_pymvpa2(subjs,first_level_fileid,out_folder = '../data/', 
                                    conditions_to_include=None,
                                    condition_count_required=None,
                                    supplementary_df = None,
                                         out_file_suffix ='',
                                    #concatenate_condition_labels=False,
                               #mask = "beta",
                               #masking_threshold=0,
                               beta_processing_args={}
                                   ):
    ## get a list of the subject folders
    sst_wt_repo = '/gpfs/projects/sanlab/shared/DEV/nonbids_data/fMRI/fx/models/SST/wave1/'
    first_level_path = sst_wt_repo + first_level_fileid + "/"
    print(first_level_path)
    subj_count = len(subjs)
    ## iterate through them
    subjs.sort()
    bd_dict={}
    #get the brain data from the beta files
    for sl in subjs:
        print(sl)
        
        #get the design data
        
        #load the matrix associated with this file
        print(first_level_path + 'sub-' + sl +'/SPM.mat')
        sl_mat = scipy.io.loadmat(
            first_level_path + 'sub-' + sl +'/SPM.mat',
            simplify_cells=True            
        )

        #convert from an SPM.mat file into a dataframe list of the betas
        beta_dict_list = []
        mat_betas = sl_mat['SPM']['Vbeta']
        for beta_i in range(len(mat_betas)):
            beta = mat_betas[beta_i]
            b_description = beta['descrip']
            condition_label = re.search('Sn\(1\)\s(.*)\*bf\(1\)',b_description)
            if (condition_label is not None):
                beta_dict_list = beta_dict_list + [{
                    'condition_index':beta_i,
                    'condition_label':condition_label.group(1),
                    'raw_beta_description':beta['descrip'],
                    'beta':beta['fname']
                }]
        #    print(condition_label)
        beta_df = pd.DataFrame(beta_dict_list)

        #fill in the details related to the subject
        beta_df['subject']=sl
        beta_df['wave']=1
        
        if conditions_to_include is not None:
            #cut down conditions to just those specified
            #also ensures that the beta_df is in the ORDER SPECIFIED in conditions_to_include
            #beta_df = beta_df.loc[beta_df.condition_label.isin(conditions_to_include),]
            beta_df = pd.concat([beta_df.loc[beta_df.condition_label==cti,] for cti in conditions_to_include])

        if condition_count_required is not None:
            if beta_df.shape[0]<condition_count_required:
                print("not enough conditions for subject "+ sl + ". Skipping this subject.")
                continue
        
        
        try: 
            #print(beta_df)
            bd = get_Brain_Data_betas_as_mvpa_for_sub(
                sl, beta_df,
                betaseries_path = first_level_path,
                events_in_design=beta_df.shape[0],
                #spatially_concatenate = concatenate_condition_labels,
                #mask = "beta" # '/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii'
                #mask = '/projects/sanlab/shared/spm12/canonical/MNI152_T1_1mm_brain_mask.nii'
#                 mask=mask,
#                 masking_threshold=masking_threshold,
                **beta_processing_args
                
            )
            
            
            bd_dict[sl]=bd
        except BehavioralDataNotFoundForBrainDataException:
            print("couldn't get data for subject " + sl + " because there was no matching behavioral data")
    
            
    
    #now append into a concatenated brain data file
    
    Brain_Data_allsubs = mvpa2.datasets.vstack(list(bd_dict.values()),a=0)#list(bd_dict.values())[0]

    #now merge in supplementary data
    sa_index_cols = ['subject','wave']
    sa_index = sa_to_df(Brain_Data_allsubs.sa,sa_index_cols)
        
    if supplementary_df is not None:
        additional_cols = pd.merge(sa_index,supplementary_df,how='left',on=['subject','wave'])
        #the merge gets us the matched values for the shape of the sample attributes
        #now we need to put them back into the sample attributes
        for cname in additional_cols.columns:
            Brain_Data_allsubs.sa[cname] = additional_cols[cname]
            
    #easier to access version of the sa
    #Brain_Data_allsubs.a['get_sa_as_df'] = lambda: sa_to_df(my_test_data.sa)

    #dump
    out_filepath = (
        out_folder + 'mvpa_Dataset_' +
        #'betaseries_' +
        first_level_fileid + '_' + str(subj_count) + 'subs' + out_file_suffix + '.pkl'
    )
    print(out_filepath)

    with open(out_filepath, 'wb') as pkl_file:
        pickle.dump(Brain_Data_allsubs,pkl_file)
        
    return(Brain_Data_allsubs)

        
        

def get_Brain_Data_betas_as_mvpa_for_sub(
    sub_label,
    behavdesign_df,
    betaseries_path,
    events_in_design,
    mask = "beta",
    masking_threshold=0,
    spatially_concatenate=False,
    contrast_condition_1=None,
    contrast_condition_2=None
):
    """
    Collect a bunch of beta files for specified subjects based on a behavioral design file
    and return them
    """
    subj_behav_design = behavdesign_df[[s in sub_label for s in behavdesign_df.subject]]
    del(behavdesign_df)
    
    if (len(subj_behav_design)==0):
        raise BehavioralDataNotFoundForBrainDataException(
            "Found no behavioral data for subject " + sub_label + ". Please ensure the data exists - it is probably missing from the source.")
    elif len(subj_behav_design)!=events_in_design:
        raise Exception("For "+sub_label+", expected " +str(events_in_design) + " beta events but found " + str(len(subj_behav_design)))

    
    subject_dir = (
         betaseries_path + 'sub-' + sub_label + '/'
    )
        
    #set path for the betas

    #beta_path_sub049 = os.listdir(subject_dir)

    #iterate through the subject's beta files
    # TO DO
    #iterate through and check all the betas exist
    for betafile in subj_behav_design.beta:
        betafilepath = subject_dir + betafile
        
        #check if file exists
        if os.path.exists(betafilepath):
            print('.')
        else:
            print(betafilepath)
            raise Exception("beta " + betafile + ' does not exist at ' + betafilepath)

    print("...verified that all expected betas exist! Processing...")
    
    if mask=="beta":
        print("setting the mask to the first image in the series " + subj_behav_design.beta.iloc[0])

        with warnings.catch_warnings(record=True) as w:
            mask_path = subject_dir + subj_behav_design.beta.iloc[0]
            print(mask_path)
#             subj_mask_dataset = fmri_dataset(mask_path)
#             subj_mask_dataset.samples = np.isnan(subj_mask_dataset.samples)==False
#             mask = mvpa2.datasets.mri.map2nifti(subj_mask_dataset)
            mask = nib.load(mask_path)
            fdata = mask.get_fdata()
            fdata_notnan = np.isnan(fdata)==False
            mask=nib.nifti1.Nifti1Image(fdata_notnan,mask.affine,header=mask.header)

            #load the first image to be a mask


    #now need to ensure hte mask is in the right space

    
    if type(mask)==str:
        #import the mask

        mask = nib.load(mask)


    
    #now check to see if it's in the same space as the images.
    first_dataset_img = nib.load(subject_dir + subj_behav_design.beta.iloc[0])
    if mask.shape!=first_dataset_img.shape:
#         print(first_dataset_img.affine)
#         print(mask.affine)
#         print(type(mask))
        mask = resample_img(mask,first_dataset_img.affine,target_shape = first_dataset_img.shape)
    
    #from nilearn import plotting
    #plotting.plot_stat_map(mask)
    
    #finally, binarize the mask
    #mask_binarized = (mask.get_fdata()>masking_threshold).astype(float)
    nifti_mask_binarized = nilearn.image.binarize_img(mask,masking_threshold)
#     print(np.sum(mask_binarized==0),end=", ")
#     print(np.sum(mask_binarized>0),end=", ")
    
    #import them, but catch a very specific warning and don't show it because it gets annoying
    #https://docs.python.org/3/library/warnings.html
    with warnings.catch_warnings(record=True) as w:
        #print([subject_dir + b for b in subj_behav_design.beta])
        if (contrast_condition_1 is None) & (contrast_condition_2 is None):
            subj_data = fmri_dataset([subject_dir + b for b in subj_behav_design.beta],mask=nifti_mask_binarized)
            
#           plotting.plot_stat_map(masked_nifti = nilearn.masking.unmask(subj_data.samples,subj_data.a['mask_nifti'].value))


            #now we concatenate
            if spatially_concatenate:
                raise Exception("spatial concatenation not implemnted")
        elif (contrast_condition_1 is not None) & (contrast_condition_2 is not None):
            contrast_1_design = subj_behav_design[subj_behav_design.condition_label==contrast_condition_1]
            contrast_2_design = subj_behav_design[subj_behav_design.condition_label==contrast_condition_2]
            subj_data_1 = fmri_dataset([subject_dir + b for b in contrast_1_design.beta],mask=nifti_mask_binarized)
            subj_data_2 = fmri_dataset([subject_dir + b for b in contrast_2_design.beta],mask=nifti_mask_binarized)
            subj_data = subj_data_1
            subj_data.samples = subj_data_1.samples-subj_data_2.samples
        else:
            raise Exception("must have BOTH contrast_condition_1 and contrast_condition_2 or NEITHER")
            
        subj_data.a['mask_nifti']=nifti_mask_binarized
        subj_data.samples[np.isnan(subj_data.samples)]=0
        print(subj_behav_design)
        #populate the sample attributes with the contents of the beta data frame
        #can't simply assign becasue we want to resepct the standard format used in pymvpa
        if (contrast_condition_1 is not None) & (contrast_condition_2 is not None):
            #process wehre we're combining two images into one
            for cname in subj_behav_design.columns:
                col_data = np.unique(subj_behav_design[cname])
                if len(col_data)==1:
                    subj_data.sa[cname] = col_data
                else:
                    #if type(col_data[0])!=str: col_data = [str(x) for x in col_data]
                    #still more than one item for some reason; let's string concatenate
                    subj_data.sa[cname] = [", ".join([str(x) for x in subj_behav_design[cname]])]
                    #subj_data.sa[cname] = [col_data]
                    
            #print(subj_data.sa)
        else:
            #regular process
            for cname in subj_behav_design.columns:
                subj_data.sa[cname] = list(subj_behav_design[cname])

    return(subj_data)