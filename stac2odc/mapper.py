#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from collections import OrderedDict
from stac2odc.ioa import load_custom_configuration_file
from stac2odc.exception import EngineDefinitionNotFound


class StacMapperEngine:
    DEFAULT_ENGINE_DEFINITION = {
        'STAC09': 'engine-definitions/stac_mapper_v09.json'
    }

    def __init__(self, engine_definition_file=None, engine_type=None):
        """StacMapperEngine is a core of stac2odc tool. An engine is able to map the STAC definition to ODC definition
        Args:
            engine_definition_file (str): File with StacMapperEngine definition
            engine_type (str): Name of pre-registered StacMapperEngine definition
        """

        if not engine_definition_file:
            if engine_type:
                engine_definition_file = self.DEFAULT_ENGINE_DEFINITION[engine_type]
            else:
                raise EngineDefinitionNotFound("Any engine definition was not found")

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
                stac_value = self._get_value_by_tree_path(stac_collection, property_definition.get('from'))
                stac_value = apply_custom_mapping_in_stac_values(stac_value, property_definition.get('customMapping'))
            else:
                stac_value = self._get_value_by_tree_path(stac_collection, product_definition.get(product_property))
            self._add_value_by_tree_path(odc_product_definition, product_property, stac_value)
        return odc_product_definition

    def _get_value_by_tree_path(self, element: dict, tree_path: str):
        """This method gets value from a dict using a string path separated with points.
        e. g.
            using the following dict:
                person = {'person': {'surname': 'blabla', 'age': 25}}
            to get the surname:
                _get_value_by_tree_path(person, 'person.surname')

        Args:
            element (dict): Element to get values using tree path
            tree_path (str): String separated with points representing the tree path
        Returns:
            recovered value using tree_path
        """
        element = element.copy()
        tree_path = tree_path.split('.')

        for tree_node in tree_path:
            element = element[tree_node]
        return element

    def _add_value_by_tree_path(self, element: dict, tree_path: str, value: object) -> None:
        """Add values in dictionary using path separated with points
        Args:
            element (dict): Element where value is inserted (in-place)
            tree_path (str): String separated with points representing the tree path
            value (object): Value to be inserted
        Returns:
            None
        """
        tree_path = tree_path.split('.')

        _pelement = element
        for tree_node in tree_path:
            # walking through tree nodes
            if tree_node not in _pelement:
                _pelement[tree_node] = OrderedDict()
                if tree_node == tree_path[-1]:
                    _pelement[tree_node] = value
            _pelement = _pelement[tree_node]

    @classmethod
    def get_registered_engines(cls):
        return cls.DEFAULT_ENGINE_DEFINITION.copy()


if __name__ == '__main__':
    import os
    import yaml
    import stac

    stac_service = stac.STAC('http://brazildatacube.dpi.inpe.br/stac/', False)
    stac_collection = stac_service.collection('CB4_64_16D_STK-1')

    # custom_fields_definition = json.load(open(os.path.join(os.getcwd(), 'json-schemas/custom-field-definition.json')))

    engine = StacMapperEngine(os.path.join(os.getcwd(), 'engine-definitions/stac_mapper_v09.json'))
    odc_product = engine.map_collection_to_product(stac_collection)

    with open('stac_collection.yaml', 'w') as f:
        yaml.dump(odc_product, f)
