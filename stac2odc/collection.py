#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from collections import OrderedDict

from loguru import logger

from stac2odc.logger import logger_message
from stac2odc.mapper import StacMapperEngine


def collection2product(engine_definition_file: str, collection_definition: dict, **kwargs) -> OrderedDict:
    """Function to convert a STAC Collection JSON to ODC Product YAML

    Args:
        engine_definition_file (str): File with definitions of mapping rules
        collection_definition (dict): definition of STAC Collection to be mapper as ODC Product
    """
    is_verbose = kwargs.get('verbose')

    logger_message("start collection2product operation", logger.info, is_verbose)
    engine = StacMapperEngine(engine_definition_file)

    logger_message("Mapping STAC Collection to ODC Product", logger.info, is_verbose)
    odc_product = engine.map_collection_to_product(collection_definition)

    return odc_product
