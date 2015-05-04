#!/usr/bin/python
from utilities.slippy_maps import convert_tile_geotiff
import os
import errno
from multiprocessing import Pool
import subprocess


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def extract_xyz(fn):
    identifier = '/tiles/png/'
    idx = fn.index(identifier)
    values = fn[idx + len(identifier):].split('.')[0].split('/')

    return int(values[1]), int(values[2]), int(values[0])


def convert_column(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".png"):
                fn_in = os.path.join(root, f)
                fn_out = os.path.join(root, f).replace('png', 'tif')
                make_sure_path_exists(fn_out.rsplit(os.path.sep, 1)[0])
                xyz = extract_xyz(fn_in)
                convert_tile_geotiff(fn_in, fn_out, xyz[0], xyz[1], xyz[2])


def merge_column(path):
    fn_out = os.path.join(os.path.dirname(path),
                          path.split('/')[-1].split('.')[0] + '.tif')
    fn_in = os.path.join(path, '*.tif')
    print fn_in
    warp = 'gdalwarp %s %s' % (fn_in, fn_out)
    # warp = 'python ../lib/gdal_merge.py -o %s %s' % (fn_out, fn_in)
    print warp
    subprocess.call(warp, shell=True)

    # calc = 'gdal_calc.py -A %s --calc="200*(A>0)" --NoDataValue=0 --outfile=%s --overwrite' % fn_out
    # print calc
    # subprocess.call(calc, shell=True)


if __name__ == "__main__":
    path = '../tiles/png/5'
    columns = [os.path.join(path, o) for o in os.listdir(path) if
               os.path.isdir(os.path.join(path, o))]

    p = Pool(4)
    print columns
    p.map(convert_column, columns)

    path = '../tiles/tif/5'
    columns = [os.path.join(path, o) for o in os.listdir(path) if
               os.path.isdir(os.path.join(path, o))]
    print columns

    p = Pool(4)
    p.map(merge_column, columns)

    warp = 'gdalwarp %s %s' % (path + '/*.tif', path + '.tif')
    warp = 'python ../lib/gdal_merge.py %s -o %s' % (path + '/*.tif', path + '.tif')
    subprocess.call(warp, shell=True)


