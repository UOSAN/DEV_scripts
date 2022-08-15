import os
import glob
import re
import argparse
import numpy as np
import pandas as pd
import scipy.stats
import functools

# set subject ID from the imput 
parser = argparse.ArgumentParser(description='shuffle edge weight')
parser.add_argument(
    '--acq',
    required=True,
    action='store',
    help='acquisition id')
parser.add_argument(
    '--dv',
    required=True,
    action='store',
    help='dv name')
args = parser.parse_args()


def extract_corr_edge(acq_id):
    '''
    (str) -> DataFrame
    This function imports the correlation matrix of each subject and extract the upper triangle value, then merge all subject data into one dataframe.
    Each row represents an edge between two nodes (labeled with column node_1 & node_2), and each column represents a subject
    '''
    # set file directory parameters
    corr_dir = os.path.join(base_dir, 'baseline_analysis', 'subject_correlation', 'baseline_acq')
    corr_fileNames = glob.glob(os.path.join(corr_dir, f'*_{acq_id}_corr.csv'))
    # initiate a list for the dataframes across all subjects
    edge_corr_dfList = []

    for file in corr_fileNames: 
        sub_df = pd.read_csv(file, sep=',', header=None) # load the correlation matrix df of a given subject
        sub_id= re.split('/|_', file)[14] # extract subject id
        if sub_id not in include_sid: 
            continue
        mask = np.triu(np.ones(sub_df.shape), k = 1).astype(bool).reshape(sub_df.size) # create a mask for the upper triangle
        sub_df_stack = sub_df.stack()[mask].reset_index() # transform the upper triangle into a long-format dataset
        sub_df_stack.columns = ['node_1','node_2',sub_id] # rename the dataframe
        edge_corr_dfList.append(sub_df_stack) # store in the lits

    # merge all individual dataframe
    edge_corr_df = functools.reduce(lambda x, y: pd.merge(x, y, on=["node_1", "node_2"]), edge_corr_dfList)

    return edge_corr_df

def edge_dv_shuffle(dv_name, edge_df, shuffle_time):
    '''
    (str, DataFrame, int, int) -> DataFrame
    This function loop through each edge from the dataframe(edge_df) and calculate the Spearman rank correlation with the variable (dv_name).
    The output is a dataframe where one column represent the coefficient and the other column represent p-value
    '''

    edge_shuffle_l = []
    for edge in edge_df.index:
        weight_list = edge_df.iloc[edge, 2:]
        edge_corr_l = []
        for i in range(shuffle_time): 
            weight_shuffle = np.random.choice(weight_list, size=weight_list.size)
            edge_corr = scipy.stats.spearmanr(weight_shuffle, base_dv[dv_name], nan_policy='omit')
            edge_corr_l.append(edge_corr.correlation)
        edge_corr_df = pd.DataFrame(edge_corr_l, columns = [edge])
        edge_shuffle_l.append(edge_corr_df)

    edge_shuffle_corr_df = pd.concat(edge_shuffle_l, axis=1)

    return edge_shuffle_corr_df



# set study parameter
base_dir = '/projects/sanlab/shared/DEV/DEV_scripts/rsfMRI/'
output_dir = os.path.join(base_dir, 'baseline_analysis', 'edge_dv_shuffle')

# set a random seed for the analysis 
np.random.seed(20210901)

# extract input information
acq_id = args.acq
dv_name = args.dv

# load the physio data
base_dv = pd.read_csv(os.path.join(base_dir, 'dv_data', 'sub_data_baseline_w.csv'))

# extract the subject Ids
include_sid = list(base_dv['SID'])

# extract edge weights for the given acquisition 
edge_weight_acq = extract_corr_edge(acq_id)

# shuffle the weights 1000 times for each edges from acq 1 and compute the correlations with BMI
edge_dv_shuffle_df = edge_dv_shuffle(f'{dv_name}_s1', edge_weight_acq, 1000)
edge_dv_shuffle_df.to_csv(os.path.join(output_dir, f'{dv_name}_acq{acq_id}_shuffle.csv'),index=False, header=False)

