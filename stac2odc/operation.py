#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from collections import OrderedDict
from typing import Union, Any


# ToDo: Check parameters and create exceptions for this operation
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


# ToDo: Check parameters and create exceptions for this operation
def apply_custom_map_function(function_definition: dict, stac_values: object) -> Union[list, Any]:
    """Function to apply custom map function to STAC Values

    Args:
        function_definition (dict): Dict with informations about function definition file (key functionName) and
        function name (key functionFile)
        stac_values: (object): objects will be used as parameters in user defined function
    Returns:
        OrderedDict: Mapped elements from STAC to ODC pattern
    """

    user_defined_function = load_user_defined_function(**function_definition)

    # ToDo: Check result elements
    if isinstance(stac_values, list):
        return [user_defined_function(element) for element in stac_values]
    return user_defined_function(stac_values)
