"""
Author: Bernice Cheung 
Date: 08/19/21

This script is for computing subject level degree centrality based on baseline wholebrain Pearson correlation acorss pair-wise ROI
"""

import os
import argparse
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core import base
import seaborn as sns
import pingouin as pg
from nilearn.image import load_img
from nltools.data import Brain_Data, Design_Matrix, Adjacency
from nltools.mask import expand_mask, roi_to_brain
from nltools.stats import zscore, fdr, one_sample_permutation
from nltools.file_reader import onsets_to_dm
from nltools.plotting import component_viewer
from scipy.stats import binom, ttest_1samp
from sklearn.metrics import pairwise_distances
from copy import deepcopy
import networkx as nx
from nilearn.plotting import plot_stat_map, view_img_on_surf
from bids import BIDSLayout, BIDSValidator
import nibabel as nib

# set subject ID from the imput 
parser = argparse.ArgumentParser(description='subject level rs connectivity analysis')
parser.add_argument(
    '--sub-id',
    required=True,
    action='store',
    help='subject id')
args = parser.parse_args()

# set dataset parameter
base_dir = '/projects/sanlab/shared/DEV/'
sub_id = args.sub_id

# load correlation data
corr_dir = os.path.join(base_dir, 'DEV_scripts', 'rsfMRI', 'baseline_analysis', 'subject_correlation', 'concatenate')
corr_filename = f'{sub_id}_concat_corr.csv'
corr_mat = pd.read_csv(os.path.join(corr_dir, corr_filename), sep=',', header=None).to_numpy()

# soft thresholding the partial correlation
roi_corr_thresholded = np.power(((corr_mat + 1) / 2 ),6)

# fisher r to z transform
roi_corr_thresholded_z = np.arctanh(roi_corr_thresholded)

# create a weighted adjacency matrix
a = Adjacency(roi_corr_thresholded_z, matrix_type='similarity', labels=[x for x in range(246)])

# generate a network 
G = a.to_graph()
node_and_degree = G.degree()

# create weighted edges
strength = G.degree(weight='weight')
strengths = {node: val for (node, val) in strength}
nx.set_node_attributes(G, dict(strength), 'strength') # Add as nodal attribute

# convert the strength into a data frame
strength_df = pd.DataFrame(list(strengths.values()), columns = [sub_id])
# export the df
fileName = sub_id + '_' + 'strength_full.csv'
output_dir = os.path.join(base_dir, 'DEV_scripts', 'rsfMRI', 'baseline_analysis', 'subject_connectivity_full', fileName)
strength_df.to_csv(output_dir, index=False)

# Normalized node strength values 1/N-1
normstrenghts = {node: val * 1/(len(G.nodes)-1) for (node, val) in strength}
nx.set_node_attributes(G, normstrenghts, 'strengthnorm') # Add as nodal attribute

# convert the normalized strength into a data frame
normstrength_df = pd.DataFrame(list(normstrenghts.values()), columns = [sub_id])
# export the df
fileName = sub_id + '_' + 'normstrength_full.csv'
output_dir = os.path.join(base_dir, 'DEV_scripts', 'rsfMRI', 'baseline_analysis', 'subject_connectivity_full', fileName)
normstrength_df.to_csv(output_dir, index=False)