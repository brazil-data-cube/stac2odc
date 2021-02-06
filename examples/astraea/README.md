# Astraea Engine Example

This is the page that presents an example of the use of `stac2odc` for indexing the Landsat-8/OLI data products available on the [Astraea.Earth](https://eod-catalog-svc-prod.astraea.earth) portal in an Open Data Cube instance.

For the realization of this example, the definition of an engine with the rules for the mapping of Products and Datasets was made. The files are:

- [stac_mapper_astraea.json](engines/stac_mapper_astraea.json): File with the description of the mapping engine and its rules
- [custom_functions.py](engines/custom_functions.py): File with the auxiliary functions used for mapping custom fields coming from STAC

Below are examples for the indexation of Products and Datasets.

**Mapping collection to ODC Product**

The first step in using the tool is indexing the collection into an ODC Product. This will be done using the `collection2product` function available in stac2odc. Below is presented the use of this command for the indexation of the collection.

```shell
stac2odc collection2product \
            -c landsat8_l1tp \
            --url https://eod-catalog-svc-prod.astraea.earth \
            --outdir ./astraea \
            --engine-file examples/astraea/engines/stac_mapper_astraea.json \
            --verbose
```

With the command's execution, log messages will be displayed indicating that the new Product is being added. The messages should look like the following

```
2021-02-05 19:30:27.277 | INFO     | stac2odc.logger:logger_message:20 - start collection2product operation
2021-02-05 19:30:27.277 | INFO     | stac2odc.logger:logger_message:20 - Mapping STAC Collection to ODC Product
2021-02-05 19:30:27.456 | INFO     | stac2odc.logger:logger_message:20 - Adding landsat8_l1tp
```

After the command finishes its execution, the new Product will already be indexed and ready to use. To check if the indexing was done correctly consult the products in your Open Data Cube instance using `datacube product list`. The product `landsat8_l1tp` must be presented.

```
landsat8_l1tp  Landsat 8 Collection 1 Tier 1 Precision Terrain from Landsat 8 Operational Land Imager (OLI) and Thermal Infrared Sensor (TIRS) data
```

**Indexing STAC Assets as ODC Datasets**

With the Product added, it will now be made the addition of Datasets associated with it. For this, the `item2dataset` command will be used. This command consumes the information present in the engine's description file and then performs the indexing of data in the Open Data Cube instance.

```shell
stac2odc item2dataset \
        --stac-collection landsat8_l1tp \
        --dc-product landsat8_l1tp \
        --url https://eod-catalog-svc-prod.astraea.earth \
        --outdir ./astraea \
        --max-items 25 \
        --engine-file examples/astraea/engines/stac_mapper_astraea.json \
        --verbose
```
