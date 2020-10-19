from stac2odc.item import item2dataset
from stac2odc.mapper import StacMapperEngine
from stac2odc.toolbox import create_feature_collection_from_stac_elements, datacube_index, \
    write_odc_element_in_yaml_file

if __name__ == '__main__':
    import os
    import stac

    stac_service = stac.STAC('https://eod-catalog-svc-prod.astraea.earth', False)
    stac_collection = stac_service.collection('landsat8_l1tp')

    engine = StacMapperEngine(os.path.join(os.getcwd(), 'engine-definitions/stac_mapper_astraea.json'))
    odc_product = engine.map_collection_to_product(stac_collection)

    features = create_feature_collection_from_stac_elements(stac_service, 2, {"collections": "landsat8_l1tp"})
    engine_definition = os.path.join(os.getcwd(), 'engine-definitions/stac_mapper_astraea.json')

    dc_index = datacube_index()
    odc_datasets = item2dataset(engine_definition, 'landsat8_l1tp', features, dc_index, is_verbose=True)

    # odc_product = engine.add_custom_fields_to_odc_element(stac_collection, odc_product,
    #                                                                           custom_fields_definition, "product")

    # write_odc_element_in_yaml_file(odc_product, './teste/stac_collection.yaml')
    write_odc_element_in_yaml_file(odc_datasets, './teste/')
