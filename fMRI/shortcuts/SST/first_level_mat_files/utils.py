
import socket

import yaml


def read_yaml_for_host(file_path):
    hostname = socket.gethostname()
    with open(file_path, "r") as f:
        return yaml.safe_load(f)[hostname]

        