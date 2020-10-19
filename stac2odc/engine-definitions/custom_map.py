from collections import OrderedDict
from typing import List, Union


def functionToMapL8Assets(collection_element: object) -> Union[List[OrderedDict], OrderedDict]:
    """Custom function to map astraea STAC 0.9
    Args:
        collection_element:
    Returns:
    """
    odc_result = []

    for key in collection_element:
        measurement_item = OrderedDict()
        stac_element = collection_element[key]

        measurement_item['name'] = key
        if 'eo:bands' in stac_element:
            measurement_item['aliases'] = [stac_element['eo:bands'][0]['common_name']]
        measurement_item['dtype'] = 'float32'
        measurement_item['nodata'] = -9999

        odc_result.append(measurement_item)

    return odc_result
