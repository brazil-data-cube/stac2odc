#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import os

import click
import stac
from datacube.index import MissingRecordError
from datacube.index.hl import Doc2Dataset
from datacube.scripts.dataset import remap_uri_from_doc, dataset_stream
from datacube.ui.common import ui_path_doc_stream
from datacube.utils import InvalidDocException
from datacube.utils.documents import read_documents
from loguru import logger

import stac2odc.collection
import stac2odc.item
from stac2odc.logger import logger_message
from stac2odc.toolbox import write_odc_element_in_yaml_file, datacube_index, prepare_advanced_filter, \
    create_feature_collection_from_stac_elements


@click.group()
def cli():
    """
    :return:
    """
    pass


@cli.command(name="collection2product", help="Function to convert a STAC Collection JSON to ODC Product YAML")
@click.option('-c', '--collection', required=True, help='Collection name (Ex. CB4MOSBR_64_3M_STK).')
@click.option('--url', default='http://brazildatacube.dpi.inpe.br/stac/', help='BDC STAC url.')
@click.option('-o', '--outdir', default=None, help='Output directory', required=True)
@click.option('-e', '--engine-file', required=True,
              help='Mapper configurations to convert STAC Collection to ODC Product')
@click.option('--datacube-config', '-dconfig', default=None, required=False)
@click.option('--verbose', default=False, is_flag=True, help='Enable verbose mode')
def collection2product_cli(collection: str, url: str, outdir: str, engine_file: str, datacube_config: str,
                           verbose: bool):
    collection_definition = stac.STAC(url, False).collection(collection)
    odc_element = stac2odc.collection.collection2product(engine_file, collection_definition, verbose=verbose)
    product_definition_file = write_odc_element_in_yaml_file(odc_element, os.path.join(outdir, f'{collection}.yaml'))

    # code adapted from: https://github.com/opendatacube/datacube-core/blob/develop/datacube/scripts/product.py
    for path_descriptor, parsed_doc in read_documents(*[product_definition_file]):
        try:
            dc_index = datacube_index(datacube_config)
            _type = dc_index.products.from_doc(parsed_doc)

            logger_message(f'Adding {_type.name}', logger.info, verbose)
            dc_index.products.add(_type)
        except InvalidDocException as e:
            logger_message(f'Error to add product: {str(e)}', logger.warning, True)


@cli.command(name="item2dataset", help="Function to convert a STAC Collection JSON to ODC Dataset YAML")
@click.option('-sc', '--stac-collection', required=True, help='Collection name (e.g. CB4MOSBR_64_3M_STK).')
@click.option('-dp', '--dc-product', required=True, help='Product name in Open Data Cube (e.g. CB4MOSBR_64_3M_STK)')
@click.option('--url', default='http://brazildatacube.dpi.inpe.br/stac/', help='BDC STAC url.')
@click.option('-o', '--outdir', default='./', help='Output directory')
@click.option('-m', '--max-items', help='Max items', required=True)
@click.option('-e', '--engine-file', required=True,
              help='Mapper configurations to convert STAC Collection to ODC Product')
@click.option('--datacube-config', '-dconfig', default=None, required=False)
@click.option('--verbose', default=False, is_flag=True, help='Enable verbose mode')
@click.option('--advanced-filter', default=None, help='Search STAC Items with specific parameters')
def item2dataset_cli(stac_collection, dc_product, url, outdir, max_items, engine_file, datacube_config, verbose,
                     advanced_filter):
    _filter = {"collections": [stac_collection]}
    if advanced_filter:
        _filter = {
            **_filter, **prepare_advanced_filter(advanced_filter)
        }

    stac_service = stac.STAC(url, False)
    dc_index = datacube_index(datacube_config)

    features = create_feature_collection_from_stac_elements(stac_service, int(max_items), _filter)
    odc_datasets = stac2odc.item.item2dataset(engine_file, dc_product, features, dc_index, verbose=verbose)
    odc_datasets_definition_files = write_odc_element_in_yaml_file(odc_datasets, outdir)

    # add datasets definitions on datacube index
    # code adapted from: https://github.com/opendatacube/datacube-core/blob/develop/datacube/scripts/dataset.py
    ds_resolve = Doc2Dataset(dc_index, [dc_product])
    doc_stream = remap_uri_from_doc(ui_path_doc_stream(odc_datasets_definition_files, uri=True))
    datasets_on_stream = dataset_stream(doc_stream, ds_resolve)

    logger_message(f"Adding datasets", logger.info, True)
    for dataset in datasets_on_stream:
        try:
            dc_index.datasets.add(dataset, with_lineage=True)
        except (ValueError, MissingRecordError):
            logger_message(f"Error to add dataset ({dataset.local_uri})", logger.warning, True)
