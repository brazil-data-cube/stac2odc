#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import yaml
from collections import OrderedDict


def setup_ordered_yaml_representation():
    """Function to setup ordered configuration for YAML generated from OrderedDict

    See:
        https://stackoverflow.com/a/8661021
    """

    def represent_dict_order(self, data): return self.represent_mapping(
        'tag:yaml.org,2002:map', data.items())
    yaml.add_representer(OrderedDict, represent_dict_order)


setup_ordered_yaml_representation()
