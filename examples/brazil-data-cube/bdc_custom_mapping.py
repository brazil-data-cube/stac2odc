from collections import OrderedDict
from typing import List, Union


def function_to_map_bdc_measurements(collection_element: object) -> Union[List[OrderedDict], OrderedDict]:
    pass


def transform_id(collection_element: object):
    return collection_element.replace("-", "_")
