import socket
import os
import yaml

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
