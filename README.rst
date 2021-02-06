stac2odc
=========

.. image:: https://img.shields.io/github/license/brazil-data-cube/stac2odc.svg
        :target: https://github.com/brazil-data-cube/bdc-odc/blob/master/LICENSE
        :alt: Software License


.. image:: https://img.shields.io/badge/lifecycle-experimental-orange.svg
        :target: https://www.tidyverse.org/lifecycle/#experimental
        :alt: Software Life Cycle


.. image:: https://img.shields.io/discord/689541907621085198?logo=discord&logoColor=ffffff&color=7389D8
        :target: https://discord.com/channels/689541907621085198#
        :alt: Join us at Discord

stac2odc is a tool created to facilitate indexing data in the Open Data Cube (ODC) using the information provided by STAC catalogs.

To allow different users to enjoy the benefits of indexing data in the ODC via STAC, stac2odc was developed to support several STAC versions, with varied ways of implementing and organizing resources. This is possible thanks to engine files, which are definition files of how the mapping between STAC and ODC entities should be done.

The engine files have different keys and ways to describe the mapping that is being done. With these files, it is possible to describe the mapping with predefined functions, which have advanced and straightforward mapping options. Still, it is also possible to use customized scripts, which receive the data and allow complex rules to be described.xing products and datasets in an ODC instance.

Getting started
----------------

To start using stac2odc it is necessary to install it. The following command can be used for this activity.::

    pip install git+https://github.com/brazil-data-cube/stac2odc

or::

    git clone https://github.com/brazil-data-cube/stac2odc \
        && cd stac2odc \
        && python3 setup.py install


After installation, the tool will be ready for use::

    $ stac2odc

    Usage: stac2odc [OPTIONS] COMMAND [ARGS]...

      :return:

    Options:
      --help  Show this message and exit.

    Commands:
      collection2product  Function to convert a STAC Collection JSON to ODC...
      item2dataset        Function to convert a STAC Collection JSON to ODC...


Two operations are available with the tool

- ``collection2product``: This function is used to convert STAC Collections into ODC Products
- ``item2dataset``: This function converts STAC Assets into ODC ODC Datasets

Documentation
--------------

The complete documentation with all the options for using the tool is still being produced. However, it is possible to consume some usage examples available in the directory [examples](examples)
