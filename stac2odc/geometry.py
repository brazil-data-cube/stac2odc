#
# This file is part of stac2odc
# Copyright (C) 2020 INPE.
#
# stac2odc is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import pyproj
import shapely.geometry
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform


def _transform_crs(crs_src: str, crs_dest: str, geom: BaseGeometry) -> BaseGeometry:
    """Reproject geometry

    Args:
        crs_src (str): Actual geometry CRS
        crs_dest (str): Destiny geometry CRS
        geom (shapely.geometry.base.BaseGeometry): Shapely Geometry
    Returns:
        shapely.geometry.base.BaseGeometry: Shapely Geometry reprojected
    """
    crs_src = pyproj.CRS(crs_src)
    crs_dest = pyproj.CRS(crs_dest)

    transform_fnc = pyproj.Transformer.from_crs(crs_src, crs_dest).transform
    return transform(transform_fnc, geom)


class StacItemGeometry:
    _crsgeom = None
    _basegeom = None

    def __init__(self, geom_def: object, geom_crs: str):
        """Class to represent a Geometry defined in STAC-SPEC for Item object

        Args:
            geom_def (dict): A dict with geometry definition (In geojson or bbox format)
            geom_crs (str): CRS definition to geom
        See:
            See STACItem  definitions <https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md>
        """

        if isinstance(geom_def, BaseGeometry):
            self._basegeom = geom_def._base_geom
        elif "type" in geom_def:
            # check is a geojson
            self._basegeom = shapely.geometry.Polygon(*geom_def['coordinates'])
        else:
            # get bbox
            self._basegeom = shapely.geometry.box(*geom_def)
        self._crsgeom = geom_crs

    @staticmethod
    def from_stacitem(stacitem_definition: dict):
        """Create a new instance based-on a StacItem definition

        Args:
            stacitem_definition (dict): STACItem definition
        Returns:
            StacItemGeometry: New instance of STACItemGeometry
        """

        # EPSG:4326 is specified in STACItem spec
        _DEFAULT_CRS = 'EPSG:4326'

        for geomkey in ['geometry', 'bbox']:
            if stacitem_definition.get(geomkey):
                return StacItemGeometry(stacitem_definition.get(geomkey), geom_crs=_DEFAULT_CRS)
        raise RuntimeError("Geometry Definition (geojson and bbox) not found in STACItem!")

    def to_crs(self, crs_dest: str):
        """Function to geom crs to another

        Args:
            crs_dest (dict): Destiny CRS definition
        Returns
            StacItemGeometry: An instance of StacItemGeometry with the new defined CRS
        """

        _basegeom_tmp = _transform_crs(self._crsgeom, crs_dest, self._basegeom)
        return StacItemGeometry(_basegeom_tmp, crs_dest)

    def to_geojson(self) -> dict:
        """Transform geometry to GeoJSON

        Returns:
            dict: Dict with geojson definition
        """

        return shapely.geometry.mapping(self._basegeom)
