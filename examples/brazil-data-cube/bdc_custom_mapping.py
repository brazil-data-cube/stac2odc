#
# This file is part of stac2odc
# Copyright (C) 2021 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import os
from collections import OrderedDict
from typing import List, Union
from urllib.parse import urlparse

import rasterio as rio

from stac2odc.exception import UserDefinedFunctionError

# definitions
BDC_ACCESS_TOKEN = ""
BDC_EXCLUDED_BANDS = ["CLEAROB", "TOTALOB", "thumbnail", "PROVENANCE"]
BDC_REPOSITORY_PATH = ""
BDC_GRID_REFERENCE_BAND = "NDVI"


def __download_file(url: str, out: str) -> None:
    """Download files
    Args:
        url (str): File URL
        out (str): output file
    Returns:
        None
    """
    import tqdm
    import requests

    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(out, "wb") as f:
            pbar = tqdm.tqdm(ncols=100, unit_scale=True, unit="B",
                             leave=None, total=(int(r.headers['Content-Length'])))
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    pbar.update(len(chunk))
                    f.write(chunk)


def __download_stac_tree(stac_item, download_out):
    """Download STAC item

    Args:
        stac_item (dict): dict with STAC item informations
        **args (dict): dict with user's definition.
    See:
        Check CLI definition to know possible args
    """

    def __href_to_path(href, basepath):
        return os.path.normpath(basepath + urlparse(href).path)

    downloaded_files_path = {}

    # Generate stac tree in basepath
    _keys = list(stac_item.keys())
    basepath_repository = __href_to_path(os.path.dirname(stac_item[_keys[0]]['href']), download_out)
    os.makedirs(basepath_repository, exist_ok=True)

    for key in stac_item:
        asset = stac_item[key]
        assetpath = urlparse(asset['href']).path

        out_path = os.path.join(basepath_repository, os.path.basename(assetpath))

        downloaded_files_path[key] = {"path": out_path}
        __download_file(asset['href'] + f"?access_token={BDC_ACCESS_TOKEN}", out_path)
    return OrderedDict(downloaded_files_path)


def function_to_map_bdc_measurements_in_local_storage(collection_element: object) -> Union[
    List[OrderedDict], OrderedDict]:
    """This function changes the BDC data product mappings for local use. This function downloads data locally for
    use outside the BDC infrastructure.

    Map stac measurements to ODC Yaml structure. Specific to BDC STAC Structure.
    Args:
        collection_element (object): Object with stac features
    Returns:
        OrderedDict: Ordered Dict with path
    """

    # remove invalid keys
    for invalid_key in BDC_EXCLUDED_BANDS: del collection_element[invalid_key]
    return __download_stac_tree(collection_element, BDC_REPOSITORY_PATH)


def get_grids_for_one_asset(collection_element: object) -> Union[List[OrderedDict], OrderedDict]:
    asset_reference = collection_element.get(BDC_GRID_REFERENCE_BAND)

    if not asset_reference:
        raise UserDefinedFunctionError("`BDC_GRID_REFERENCE_BAND` not found!")
    datasource = rio.open(asset_reference["href"] + f"?access_token={BDC_ACCESS_TOKEN}")

    return OrderedDict({
        "default": {
            "shape": list(datasource.shape),
            "transform": list(datasource.transform)
        }
    })


def transform_id(collection_element: object):
    return collection_element.replace("-", "_")
