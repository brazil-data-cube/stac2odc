#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from collections import OrderedDict

import stac2odc.tree as tree
from stac2odc.exception import ODCInvalidType
from stac2odc.io_yaml import load_custom_configuration_file
from stac2odc.operation import apply_custom_map_function


class StacMapperEngine:
    def __init__(self, engine_definition_file=None):
        """StacMapperEngine is a core of stac2odc tool. An engine is able to map the STAC definition to ODC definition
        Args:
            engine_definition_file (str): File with StacMapperEngine definition
        """
        self._engine_definition = load_custom_configuration_file(engine_definition_file)

    def map_collection_to_product(self, stac_collection: dict):
        """Method to map STAC Collections to Products using engine's selected rules
        Args:
            stac_collection (dict): STAC Collection properties
        Returns:
            OrderedDict: ODC Product created using STAC Collection definitions
        """

        def apply_custom_mapping_in_stac_values(stac_values: list, custom_mapping: dict):
            """Function to map custom definitions in mapping function. With this functions is possible use STAC
            definition in arbitrary fields
            Args:
                stac_values (list): List of STAC Items
                custom_mapping (dict): Dict with custom mapping, where key is used in ODC's definition and values is
                recovered from STAC elements

            Returns:
                list: List with STAC Items mapped
            """
            stac_values_with_custom_fields = []
            for _stac_value in stac_values:
                _stac_value_to_map = OrderedDict()

                for custom_key_mapping in custom_mapping:
                    _stac_value_to_map[custom_key_mapping] = _stac_value.get(
                        custom_mapping.get(custom_key_mapping)
                    )
                stac_values_with_custom_fields.append(_stac_value_to_map)
            return stac_values_with_custom_fields

        odc_product_definition = OrderedDict()
        collection_mapper = self._engine_definition.get('collection')
        product_definition = collection_mapper.get('fromSTAC')

        for product_property in product_definition:
            property_definition = product_definition.get(product_property)

            if 'customMapping' in property_definition:
                stac_value = tree.get_value_by_tree_path(stac_collection, property_definition.get('from'))
                stac_value = apply_custom_mapping_in_stac_values(stac_value, property_definition.get('customMapping'))
            elif 'customMapFunction' in property_definition:
                property_is_from = property_definition.get('from')

                stac_value = tree.get_value_by_tree_path(stac_collection, property_is_from)
                stac_value = apply_custom_map_function(property_is_from, stac_value,
                                                       property_definition.get('customMapFunction'))
            else:  # normal code
                stac_value = tree.get_value_by_tree_path(stac_collection, product_definition.get(product_property))
            tree.add_value_by_tree_path(odc_product_definition, product_property, stac_value)
        return self._add_custom_fields_to_odc_element(odc_product_definition, "collection")

    def _add_custom_fields_to_odc_element(self, odc_element: OrderedDict, odc_element_type: str) -> OrderedDict:
        """Add custom fields into ODC Elements (Products or Datasets) in arbitrary tree paths
        Args:
            odc_element (OrderedDict): Element where value is inserted (in-place)
            odc_element_type (str): Name of odc element where values is inserted. It has to be the same value defined
            in custom_fields_obj
        Returns:
            OrderedDict: ODC Element with custom fields inserted
        """
        if not self._engine_definition.get(odc_element_type, None):
            raise ODCInvalidType(f"ODC Type {odc_element_type} is not avaliable in custom fields definition!")

        mapper = self._engine_definition.get(odc_element_type)

        from_file_definitions = mapper.get('fromFile', None)
        from_constant_definitions = mapper.get('fromConstant', None)

        # adding constants definitions
        if from_constant_definitions:
            for constant_product_definition in from_constant_definitions:
                tree_path = constant_product_definition.split(".")
                _value = from_constant_definitions.get(constant_product_definition)
                if len(tree_path) > 1:  # check if tree_path go to a list of elements
                    _odc_prod_def = odc_element.copy()
                    for tp in tree_path[:-1]:
                        _odc_prod_def = _odc_prod_def.get(tp)
                        if isinstance(_odc_prod_def, list):
                            for el in _odc_prod_def:
                                key = list(el.keys())[0]
                                tree.add_value_by_tree_path(odc_element, ".".join([tp, el.get(key), tree_path[-1]]),
                                                            _value)
                else:
                    tree.add_value_by_tree_path(odc_element, constant_product_definition, _value)

        if from_file_definitions:
            for odc_element_property in from_file_definitions:
                value = load_custom_configuration_file(
                    from_file_definitions.get(odc_element_property).get('file')
                )
                tree.add_value_by_tree_path(odc_element, odc_element_property, value)

        return odc_element

    def map_item_to_dataset(self, stac_collection: dict):
        """
        Args:
            stac_collection:

        Returns:
        """
        pass
