import socket
import os
import yaml
import numpy as np

def read_yaml_for_host(file_path):
    hostname = socket.gethostname()
    #print full current working directory
    #print("current working directory: " + os.getcwd())
    #read yaml file
    with open(file_path, 'r') as f:
        yaml_full = yaml.safe_load(f)
    
    if hostname in yaml_full:
        yaml_host = yaml_full[hostname]
    else:
        print("yaml file does not contain host-specific settings for this host. Using default settings.")
        yaml_host = yaml_full['default']
    
    return(yaml_host)


def get_2DX_from_4DX(nifti_X):

    #rotate my array so that the last dimension is first
    print(nifti_X.shape)
    nifti_X=np.moveaxis(nifti_X,-1,0)
    print(nifti_X.shape)
    pre_reshaped_shape = nifti_X.shape
    #now flatten dims 2-4 into a single dimension
    arr2d_full=nifti_X.reshape([nifti_X.shape[0],np.prod(nifti_X.shape[1:4])])
    print("this is the form of the data that the decoder wants, (n_samples, n_features)")
    print(arr2d_full.shape)
    return(arr2d_full)


def get_4DX_from_2DX(arr2d,pre_reshaped_shape):
    #now undo the above operations to get the original matrix
    arr4d=arr2d.reshape(pre_reshaped_shape)
    print(arr4d.shape)
    arr4d=np.moveaxis(arr4d,0,-1)
    print(arr4d.shape)
    return(arr4d)