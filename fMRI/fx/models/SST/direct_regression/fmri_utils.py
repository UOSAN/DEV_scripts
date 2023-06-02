from socket import gethostname
from yaml.loader import SafeLoader
import yaml
import glob
import pandas as pd
import re

def load_config(config_path = None):
    if config_path is None: config_path = 'config.yml'
    print(gethostname(),flush=True)
    # Open the file and load the file
    with open(config_path) as f:
        all_yaml = yaml.load(f, Loader=SafeLoader)
        if gethostname() in all_yaml.keys():
            config = all_yaml[gethostname()]
        else:
            config = all_yaml['default']
            
    print(config,flush=True)
    return(config)
            

def get_mask_df_from_mask_locations(mask_locations):
    mask_paths = []
    for mask_location in mask_locations:
        mask_paths_i = glob.glob(mask_location+"*.nii*")
        mask_paths= mask_paths + mask_paths_i


    mask_labels = [re.match(".*/(.*)\.nii(\.gz)?",mp)[1] for mp in mask_paths]

    mask_df = pd.DataFrame({
        'mask_label':mask_labels,
        'mask_path': mask_paths
    })
    return(mask_df)


def print_roi_info(roi_data):
    for s in roi_data.keys():
        print(s,flush=True)
        for wave in roi_data[s].keys():
            print(wave)
            print(roi_data[s][wave].shape)
            print(roi_data[s][wave].columns,flush=True)