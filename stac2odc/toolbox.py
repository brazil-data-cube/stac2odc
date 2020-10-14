#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import json
import os
from collections import OrderedDict
from typing import Union, Any

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


def write_yaml_file(content: Union[dict, OrderedDict], path_to_file: str):
    """
    Args:
        content (dict or OrderedDict): Content to write
        path_to_file (str): Path to file where content will be write
    Returns:
        None
    """
    os.makedirs(os.path.split(path_to_file)[0], exist_ok=True)

    with open(path_to_file, 'w') as ofile:
        yaml.dump(content, ofile)
    return path_to_file


def datacube_index(datacube_config_path=None) -> Union['datacube.index.index.Index', Any]:
    """Retrieve a ODC Index connection
    Args:
        datacube_config_path (str): Path to datacube's database connection config
    Returns:
        None or datacube.index.index.Index object
    """

    import datacube.index
    import datacube.config

    datacube_config = datacube.config.LocalConfig.find(datacube_config_path)
    return datacube.index.index_connect(datacube_config, 'stac2odc')
