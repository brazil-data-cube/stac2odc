#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import uuid
from collections import OrderedDict
from typing import List, Union, Dict

import datacube.index.index
from loguru import logger
import json

import stac2odc.tree as tree
from stac2odc.logger import logger_message
from stac2odc.mapper import StacMapperEngine
import rasterio as rio


def _create_geometry_object(stac_values: Dict) -> Union[None, OrderedDict]:
    """
    Args:
        geometry_path_in_stac_values (str): Path where geometry definition is in stac_values
        stac_values (dict): Stac Item definition
        native_crs (str): Dataset native CRS
    Returns:
        OrderedDict or None
    """

    first_asset = list(stac_values.get('assets', {}).keys())[0]

    item_path = stac_values['assets'][first_asset]['href']
    
    ds = rio.open(item_path)

    coordinates =  [[
        [ds.bounds.left, ds.bounds.top],     # left, top
        [ds.bounds.right, ds.bounds.top],    # right, top
        [ds.bounds.right, ds.bounds.bottom], # right, bottom
        [ds.bounds.left, ds.bounds.bottom],  # left, bottom
        [ds.bounds.left, ds.bounds.top]      # left, top
    ]]           

    return OrderedDict({
        "type": "Polygon",
        "coordinates": coordinates  
    })


def item2dataset(engine_definition_file: str, collection_name: str,
                 item_collection_definition: List, dc_index: datacube.index.index.Index = None, **kwargs) -> \
        Union[List[OrderedDict], OrderedDict]:
    """Function to convert a STAC Collection JSON to ODC Dataset YAML

    Args:
        engine_definition_file (str): File with definitions of mapping rules
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
    engine = StacMapperEngine(engine_definition_file)

    odc_elements = []
    logger_message("mapping each STAC item in STAC Item Collection", logger.info, is_verbose)
    for item_definition in item_collection_definition:
        _odc_element = engine.map_item_to_dataset(item_definition)
        _odc_element["product"] = OrderedDict({
            "name": collection_name
        })

        # create id based on odc_element content to avoid multiple inserts
        _odc_element["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(_odc_element)))

        # geometry is only mapped if 'crs' is defined in product
        if 'geometry' in _odc_element:
            del _odc_element['geometry']

        if dc_index:
            # get product definition
            crs_definition = 'storage.crs'
            product_definition = dc_index.products.get_by_name(collection_name).definition

            if tree.is_path_valid_in_tree(product_definition, crs_definition):
                _native_crs = tree.get_value_by_tree_path(product_definition, crs_definition)
                _odc_element["crs"] = _native_crs

                # get geometry metadata from file
                stac_item_geometry = _create_geometry_object(item_definition)

                if stac_item_geometry:
                    def listit(t):
                        # from: https://stackoverflow.com/questions/1014352/how-do-i-convert-a-nested-tuple-of-tuples-and-lists-to-lists-of-lists-in-python
                        return list(map(listit, t)) if isinstance(t, (list, tuple)) else t

                    # transform tuples into list to avoid errors in yaml read/write
                    stac_item_geometry["coordinates"] = listit(stac_item_geometry["coordinates"])
                    _odc_element["geometry"] = stac_item_geometry
        else:
            logger_message("There is no datacube_index definition. CRS will not be defined", logger.warning, is_verbose)
        odc_elements.append(_odc_element)
    return odc_elements
