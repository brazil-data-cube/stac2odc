#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import uuid
from collections import OrderedDict
from typing import List, Union

import datacube.index.index
from loguru import logger

import stac2odc.tree as tree
from stac2odc.logger import logger_message
from stac2odc.mapper import StacMapperEngine


def item2dataset(engine: StacMapperEngine, collection_name: str,
                 item_collection_definition: List, dc_index: datacube.index.index.Index = None, **kwargs) -> \
        Union[List[OrderedDict], OrderedDict]:
    """Function to convert a STAC Collection JSON to ODC Dataset YAML

    Args:
        engine (StacMapperEngine): StacMapperEngine Instance
        collection_name (str): Name of collection
        item_collection_definition (list): Feature collected from STAC services
        dc_index (str): Instance of datacube_index. If not defined, some properties will not be defined in
        ODC dataset definition (e. g. CRS)
    See:
        See the BDC STAC catalog for more information on the collections available
        (http://brazildatacube.dpi.inpe.br/bdc-stac/0.8.0/)
    """

    is_verbose = kwargs.get('verbose')
    logger_message("start item2dataset operation", logger.info, is_verbose)

    odc_elements = []
    logger_message("mapping each STAC item in STAC Item Collection", logger.info, is_verbose)
    for item_definition in item_collection_definition:
        _odc_element = engine.map_item_to_dataset(item_definition)
        _odc_element["product"] = OrderedDict({
            "name": collection_name
        })
        _odc_element["id"] = str(uuid.uuid4())

        if dc_index:
            # get product definition
            crs_definition = 'storage.crs'
            product_definition = dc_index.products.get_by_name(collection_name).definition

            if tree.is_path_valid_in_tree(product_definition, crs_definition):
                _odc_element["crs"] = tree.get_value_by_tree_path(product_definition, crs_definition)
        else:
            logger_message("There is no datacube_index definition. CRS will not be defined", logger.warning, is_verbose)
        odc_elements.append(_odc_element)
    return odc_elements
