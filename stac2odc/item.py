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

import stac2odc.tree as tree
from stac2odc.geometry import StacItemGeometry
from stac2odc.logger import logger_message
from stac2odc.mapper import StacMapperEngine


def _create_geometry_object(geometry_path_in_stac_values: str, stac_values: Dict,
                            native_crs: str) -> Union[None, OrderedDict]:
    """
    Args:
        geometry_path_in_stac_values (str): Path where geometry definition is in stac_values
        stac_values (dict): Stac Item definition
        native_crs (str): Dataset native CRS
    Returns:
        OrderedDict or None
    """

    if geometry_path_in_stac_values:
        geometry_definition = tree.get_value_by_tree_path(stac_values, geometry_path_in_stac_values)

        if geometry_definition:
            # ESPG:4326 is a STAC Item Spec definition
            stac_item_geometry = StacItemGeometry(geometry_definition, 'EPSG:4326').to_crs(native_crs).to_geojson()

            odc_geometry = OrderedDict()
            odc_geometry['type'] = stac_item_geometry['geometries'][0]['type']
            odc_geometry['coordinates'] = str(stac_item_geometry['geometries'][0]['coordinates'])
            return odc_geometry
    return


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
                _native_crs = tree.get_value_by_tree_path(product_definition, crs_definition)
                _odc_element["crs"] = _native_crs

                # try add geometry
                # "geometry" name is defined in ODC-Dataset fields spec
                geometry_path = engine.get_definition_by_name("dataset", "fromSTAC", "geometry")
                stac_item_geometry = _create_geometry_object(geometry_path, item_definition, _native_crs)

                if stac_item_geometry:
                    _odc_element["geometry"] = stac_item_geometry
        else:
            logger_message("There is no datacube_index definition. CRS will not be defined", logger.warning, is_verbose)
        odc_elements.append(_odc_element)
    return odc_elements
