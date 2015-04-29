import math
from osgeo import ogr, osr
import tempfile
import subprocess
import uuid


def degree_to_tile_number(lat_deg, lon_deg, zoom):
    """
    Converts a latitude, longitude and zoom to a tile number.
    :param lat_deg:
    :param lon_deg:
    :param zoom:
    :return: Tuple of column and row
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x, y


def tile_number_to_degree(x, y, zoom):
    """
    Takes a slippy tile number and zoom and returns the NW corner.
    :param x: float
    :param y: float
    :param zoom: 0 - 21
    :return: Tuple
    """
    n = 2.0 ** zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def tile_bounds(x, y, zoom):
    """
    Returns the bounds of the tile.
    :param x: float
    :param y: float
    :param zoom: integer 0-21
    :return: Tuple of tuples
    """
    return tile_number_to_degree(x, y, zoom), tile_number_to_degree(x + 1, y + 1, zoom)


def project_point(x, y, s_srs=4326, t_srs=3857):
    source = osr.SpatialReference()
    source.ImportFromEPSG(s_srs)

    target = osr.SpatialReference()
    target.ImportFromEPSG(t_srs)

    transform = osr.CoordinateTransformation(source, target)
    point = ogr.CreateGeometryFromWkt("POINT (%f %f)" % (y, x))
    point.Transform(transform)

    return point.GetPoint()


def convert_tile_geotiff(fn_in, fn_out, x, y, zoom, t_srs="EPSG:4326"):
    """
    :param fn_in: name of file
    :param fn_out: name of file
    :return: None
    """

    # get bounds of tile in lat, lon
    t_bounds = tile_bounds(x, y, zoom)

    # convert back to epsg:3857
    s_bounds = (project_point(t_bounds[0][0], t_bounds[0][1]),
                project_point(t_bounds[1][0], t_bounds[1][1]))

    # get temp filename
    fn_tmp = tempfile.gettempdir() + '/' + str(uuid.uuid4()) + '.tif'

    # from png create geotiff in epsg:3857
    translate = 'gdal_translate %s %s -a_srs %s -a_ullr %f %f %f %f' % (
        fn_in, fn_tmp, 'EPSG:3857', s_bounds[0][0], s_bounds[0][1], s_bounds[1][0],
        s_bounds[1][1] )
    subprocess.call(translate, shell=True)
    
    # project geotiff to epsg:4326
    warp = 'gdalwarp -s_srs EPSG:3857 -t_srs %s %s %s' % (t_srs, fn_tmp, fn_out)
    subprocess.call(warp, shell=True)
