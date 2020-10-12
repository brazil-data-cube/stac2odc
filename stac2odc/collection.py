#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import yaml
from loguru import logger

from stac2odc.logger import logger_message
from stac2odc.mapper import StacMapperEngine


def collection2product(engine_definition_file: str, collection_definition: dict, outfile: str, **kwargs) -> None:
    """Function to convert a STAC Collection JSON to ODC Product YAML

    Args:
        engine_definition_file (str): File with definitions of mapping rules
        collection_definition (dict): definition of STAC Collection to be mapper as ODC Product
        outfile (str): file to write output result
    """
    is_verbose = kwargs.get('verbose')

    logger_message("start collection2product operation", logger.info, is_verbose)
    engine = StacMapperEngine(engine_definition_file)

    logger_message("Mapping STAC Collection to ODC Product", logger.info, is_verbose)
    odc_product = engine.map_collection_to_product(collection_definition)

    logger_message("Writing the result!", logger.info, is_verbose)
    with open(outfile, 'w') as ofile:
        yaml.dump(odc_product, ofile)
