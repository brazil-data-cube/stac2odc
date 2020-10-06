import json
import yaml


def load_custom_configuration_file(custom_configuration_file_path: str):
    """Load custom config file in JSON or YAML format

    Args:
        custom_configuration_file_path (str): absolute path to file
    Returns:
        dict: Configuration file in dict format
    """

    with open(custom_configuration_file_path, 'r') as cfile:
        loader = json
        if '.yaml' in custom_configuration_file_path:
            loader = yaml
        return loader.load(cfile)
