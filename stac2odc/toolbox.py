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
from typing import Union, Any, List

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


def write_odc_element_in_yaml_file(content: Union[dict, OrderedDict, List[OrderedDict]],
                                   path_to_file: str) -> Union[str, List]:
    """
    Args:
        content (dict or OrderedDict): Content to write
        path_to_file (str): Path to file where content will be write
    Returns:
        None
    """

    def _write(path_to_file, content):
        with open(path_to_file, 'w') as ofile:
            yaml.dump(content, ofile)

    os.makedirs(path_to_file, exist_ok=True)

    if isinstance(content, list):
        element_paths = []
        for c in content:
            _path = os.path.join(path_to_file, c['id'] + ".yaml")
            _write(_path, c)
            element_paths.append(_path)
        return element_paths
    else:
        _write(path_to_file, content)
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


def create_feature_collection_from_stac_elements(stac_service, max_items: int, advanced_filter: dict) -> List:
    """Create list with all stac features avaliable in STAC.

    Args
        stac_service (stac.STAC): STAC Service instance
        max_items (int): Max items recovered from STAC
        advanced_filter (dict): Filter with STAC parameters to recovery feature collection
    Returns:
        List: List of features recovered from STAC
    """

    stac_max_page = 99999999

    limit = 120
    total_items = 0
    features_recovered_from_search = []
    for page in range(1, stac_max_page + 1):
        if max_items is not None and max_items == total_items:
            break

        if limit > (max_items - total_items):
            limit = (max_items - total_items)

        features = stac_service.search({
            **advanced_filter, **{
                "page": page,
                "limit": limit
            }
        }).features
        features_recovered_from_search.extend(features)

        if len(features) == 0 or len(features_recovered_from_search) >= max_items:
            break
    return features_recovered_from_search


def prepare_advanced_filter(filter_options: str) -> dict:
    """Prepare a region geometry from file or string
    Args:
        filter_options: geometry str or file path to geometry.

        >> filter_options = {'intersects': {'type': 'Point', 'coordinates': [-45, -13]}}
        >> filter_options = '/path/to/geom.json
    Returns:
    """
    import ast
    import json

    if filter_options:
        if os.path.isfile(filter_options):
            with open(filter_options, 'r') as f:
                filter_options = json.load(f)
            # advanced filter do not specify collections!
            if 'collections' in filter_options:
                del filter_options['collections']
        else:
            filter_options = ast.literal_eval(filter_options)
        return filter_options
    return None
