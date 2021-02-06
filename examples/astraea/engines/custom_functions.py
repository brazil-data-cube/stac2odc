from collections import OrderedDict
from typing import List, Union, Dict

import rasterio as rio

from stac2odc.exception import UserDefinedFunctionError

ASTRAEA_GRID_REFERENCE_BAND = "B1"

ASTRAEA_INVALID_KEYS = ["thumb_small", "thumb_large", "MTL", "ANG"]


def remove_invalid_keys(dict_in: Dict, invalid_keys: list) -> Dict:
    """Remove invalid keys from dict

    Args:
        dict_in (Dict): Dictionary to remove keys

        invalid_keys (list): List of keys to remove in `dict_in`
    Returns:
        Dict: Dict without invalid keys
    """
    _dict = dict_in.copy()

    for invalid_key in invalid_keys:
        if invalid_key in _dict:
            del _dict[invalid_key]
    return _dict


def functionToMapL8Assets(collection_element: object) -> Union[List[OrderedDict], OrderedDict]:
    """Custom function to map astraea STAC 0.9
    Args:
        collection_element (object): Element from STAC. Is the same specified by user
    Returns:
        Union[List[OrderedDict], OrderedDict]: Must be return a list of OrderedDict or OrderedDict
    """
    odc_result = []

    for key in remove_invalid_keys(collection_element, ASTRAEA_INVALID_KEYS):
        measurement_item = OrderedDict()
        stac_element = collection_element[key]

        measurement_item['name'] = key
        if 'eo:bands' in stac_element:
            measurement_item['aliases'] = [stac_element['eo:bands'][0]['common_name']]
        measurement_item['dtype'] = 'float32'
        measurement_item['nodata'] = -9999

        odc_result.append(measurement_item)

    return odc_result


def get_grid(collection_element: object) -> Union[List[OrderedDict], OrderedDict]:
    asset_reference = collection_element.get(ASTRAEA_GRID_REFERENCE_BAND)

    if not asset_reference:
        raise UserDefinedFunctionError("`ASTRAEA_GRID_REFERENCE_BAND` not found!")
    datasource = rio.open(asset_reference["href"])

    return OrderedDict({
        "default": {
            "shape": list(datasource.shape),
            "transform": list(datasource.transform)
        }
    })
