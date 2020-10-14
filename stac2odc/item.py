#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from collections import OrderedDict
from typing import List, Union

from loguru import logger

from stac2odc.logger import logger_message


def item2dataset(engine_definition_file: str,
                 item_collection_definition: list, **kwargs) -> Union[List[OrderedDict], OrderedDict]:
    """Function to convert a STAC Collection JSON to ODC Dataset YAML

    Args:
        engine_definition_file (str): File with definitions of mapping rules
        item_collection_definition (list): Feature collected from STAC services

    See:
        See the BDC STAC catalog for more information on the collections available
        (http://brazildatacube.dpi.inpe.br/bdc-stac/0.8.0/)
    """

    is_verbose = kwargs.get('verbose')

    logger_message("start item2dataset operation", logger.info, is_verbose)
