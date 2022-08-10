'''
This script is to generate whole brain connectivity with pariwise correlation from the coefficient output generated by subject_corr.py
'''

import os
import argparse
import numpy as np
import pandas as pd
from nltools.data import Adjacency
import networkx as nx

# set subject ID from the imput 
parser = argparse.ArgumentParser(description='subject level rs connectivity analysis')
parser.add_argument(
    '--sub-id',
    required=True,
    action='store',
    help='subject id')
args = parser.parse_args()

# set dataset parameter
base_dir = '/projects/sanlab/shared/DEV'
sub_id = args.sub_id

# load correlation data
corr_dir = os.path.join(base_dir, 'DEV_scripts','rsfMRI', 'baseline_analysis', 'subject_correlation', 'concatenate')
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
fileName = sub_id + '_' + 'strength_corr.csv'
output_dir = os.path.join(base_dir, 'DEV_scripts','rsfMRI', 'baseline_analysis', 'subject_connectivity', fileName)
strength_df.to_csv(output_dir, index=False)

# Normalized node strength values 1/N-1
normstrenghts = {node: val * 1/(len(G.nodes)-1) for (node, val) in strength}
nx.set_node_attributes(G, normstrenghts, 'strengthnorm') # Add as nodal attribute

# convert the normalized strength into a data frame
normstrength_df = pd.DataFrame(list(normstrenghts.values()), columns = [sub_id])
# export the df
fileName = sub_id + '_' + 'normstrength_corr.csv'
output_dir = os.path.join(base_dir, 'DEV_scripts','rsfMRI', 'baseline_analysis', 'subject_connectivity', fileName)
normstrength_df.to_csv(output_dir, index=False)