"""
Takes a raster image and creates a polygon around pixel values, excluding NULL
"""

import os

import fiona
import rasterio
from rasterio.features import shapes
from shapely.geometry import mapping, shape
from shapely.ops import cascaded_union



def create_geometry(raster_input):
    """
    Creates a shapely polygon from a raster image
    :param raster_input: raster path
    :return: shapely geometry
    """
    mask = None
    results = None
    pixels = []

    # with rasterio.drivers():
    with rasterio.open(raster_input) as src:
        image = src.read(1)  # first band
        results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v)
            in enumerate(
            shapes(image, mask=mask, transform=src.affine)))

    return results


def merge_polygons(geometries):
    """
    Merge polygons that are neighbors
    :param geometries: shapely geometries (polygons)
    :return: merged polygons
    """

    results = []

    for polygon in geometries:
        polygons = shape(polygon['geometry'])
        results.append(polygons)

    print("Creating union from polygons...")
    return cascaded_union(results)


def shape_builder(raster_input, output_path):
    "Builds a polygon out of the pixel polygons"

    # polygons = []
    polygons = list(create_geometry(raster_input))
    polygons = merge_polygons(polygons)
    polygonalize_geometry(polygons, output_path)

    #for polygon in polygons:
    ##
        #input(polygon)


def polygonalize_geometry(geometry, output_path):
    """
    Creates a shapely polygon from the geometry
    :param geometry: Geometry from create_geometry()
    :return: a shapely polygon
    """

    output_file = os.path.join(os.path.dirname(output_path), "image_features.shp")
    print("Writing file {}".format(output_file))
    schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'int'}
    }

    # write the shapefile
    with fiona.open(output_file, 'w', 'ESRI Shapefile', schema) as c:
        for polygon in geometry:
            c.write({
                'geometry': mapping(shape(polygon['geometry'])),
                'properties': {'id': 123}
            })


def main_menu():
    """
    Prompts user
    :return: Runs the script
    """

    # raster_path = input("Path to raster image: ")
    raster_path = "./testData/clipped_image"

    print("Creating geometries..")
    # polygon = create_geometry(raster_path)
    polygon = shape_builder(raster_path, raster_path)

    # print(polygon)

    # print("Converting geometry to a shapely geometry...")
    # polygon = shape(polygon[0]['geometry'])
    # polygonalize_geometry(polygon, raster_path)


if __name__ == '__main__':
    main_menu()
