#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from collections import OrderedDict
from typing import List, Union

from stac2odc.exception import InvalidReturnedTypeFromUserDefinedFunction


def load_user_defined_function(function_name: str, module_file: str):
    """Function to load arbitrary functions

    Args:
        function_name (str): name of function to load from function_file
        module_file (str): file module where function is defined
    Returns:
        function loaded from file
    """

    import types
    import importlib.machinery

    loader = importlib.machinery.SourceFileLoader('user_defined_module', module_file)
    module = types.ModuleType(loader.name)
    loader.exec_module(module)

    return getattr(module, function_name)


def apply_custom_map_function(stac_element_name: str,
                              stac_values: object, function_definition: dict) -> Union[List[OrderedDict], OrderedDict]:
    """Function to apply custom map function to STAC Values

    Args:
        stac_element_name (str): Key name where values from
        function_definition (dict): Dict with informations about function definition file (key functionName) and
        function name (key functionFile)
        stac_values: (object): objects will be used as parameters in user defined function
    Returns:
        OrderedDict: Mapped elements from STAC to ODC pattern
    """

    user_defined_function = load_user_defined_function(function_definition['functionName'],
                                                       function_definition['functionFile'])
    odc_element_created_with_user_function = user_defined_function(stac_values)

    if not isinstance(odc_element_created_with_user_function, OrderedDict) and not isinstance(
            odc_element_created_with_user_function, list):
        tname = type(odc_element_created_with_user_function)

        raise InvalidReturnedTypeFromUserDefinedFunction(f"""
            The user defined function to {stac_element_name} is invalid! The output must be an OrderedDict or list. 
Actual return is {tname} 
        """.strip())
    return odc_element_created_with_user_function
