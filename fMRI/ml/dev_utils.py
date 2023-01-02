import socket
import yaml

def read_yaml_for_host(file_path):
    hostname = socket.gethostname()
    yaml_full = yaml.safe_load(file_path)
    if hostname in yaml_full:
        yaml_host = yaml_full[hostname]
    else:
        print("yaml file does not contain host-specific settings for this host. Using default settings.")
        yaml_host = yaml_full['default']
    
    return(yaml_host)
