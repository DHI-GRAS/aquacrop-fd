import contextlib
import logging

import rasterio.crs
import rasterio.vrt
import rasterio.windows
import affine
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)

CRS_WGS = rasterio.crs.CRS({'init': 'epsg:4326'})


def _datasets_are_congruent(datasets):
    """Determine whether datasets are congruent"""
    profiles = set((src.height, src.width, src.transform, src.crs.to_string()) for src in datasets)
    return (len(profiles) == 1), profiles


def select_extract_class_points(
        select_path, extract_path, select_class, bounds=None,
        remove_empty_extracted=True,
):
    """Find points corresponding to class

    Parameters
    ----------
    select_path : str or Path
        path to raster with classes to select
    extract_path : str or Path
        path to raster with data to extract at selected points
    select_class : int
        value for class to select
    bounds : tuple (xmin, ymin, xmax, ymax), optional
        bounds within file to search
        in lat, lon coordinates
    remove_empty_extracted : bool
        remove points where extracted data is nodata

    Yields
    ------
    xr.Dataset
        coordinates of points in selection dataset
        that are equal to select_class
        together with extracted values from extract dataset
        and indices in original image (for raster reconstruction)
    """
    with contextlib.ExitStack() as es:
        datasets = [
            es.enter_context(rasterio.open(path))
            for path in [select_path, extract_path]
        ]

        congruent, profiles = _datasets_are_congruent(datasets)
        if not congruent:
            raise ValueError(
                f'Datasets must be perfectly congruent. Got {profiles}.'
            )

        # take first dataset as model
        src = datasets[0]
        if src.crs != CRS_WGS:
            raise ValueError(f'Expecting datasets in WGS84. Got {src.crs}.')

        if bounds is not None:
            logger.debug(f'Clipping data to bounds {bounds}')
            # limit dataset to bounds
            window = src.window(*bounds)
            window = window.round_offsets().round_shape()
            transform = src.window_transform(window)
            vrts = [
                es.enter_context(rasterio.vrt.WarpedVRT(
                    src, transform=transform, width=window.width, height=window.height
                )) for src in datasets
            ]
        else:
            # pass
            vrts = datasets

        sds, xds = vrts

        # select class points
        seldata = sds.read(1)
        selcond = seldata == select_class
        if not np.any(selcond):
            raise ValueError(
                f'No points found for class value {select_class} (within bounding box).'
            )
        jj, ii = np.where(selcond)
        extracted = xds.read(1)[selcond]

        if remove_empty_extracted:
            # remove points where extracted is nodata
            good = extracted != xds.nodata
            logger.info(f'Dropping {np.sum(~good)} points where extracted data is nodata.')
            extracted = extracted[good]
            ii = ii[good]
            jj = jj[good]

        # convert pixel indices to lon, lat coordinates
        lon, lat = sds.transform * (ii, jj)

        # store all in Dataset
        variables = {'lon': lon, 'lat': lat, 'i': ii, 'j': jj, 'extracted': extracted}
        data_vars = {
            name: xr.DataArray(data, dims='point', name=name)
            for name, data in variables.items()
        }
        ds = xr.Dataset(data_vars, coords={'point': np.arange(len(lon))})
        ds.attrs.update({name: sds.profile[name] for name in ['width', 'height']})
        # properly serialize transform
        ds.attrs['transform'] = list(sds.profile['transform'])
        return ds


def interpolate_to_points(da, ixds):
    """Interpolate data array to points

    Parameters
    ----------
    da : DataArray
        data to interpolate
    ixds : Dataset
        dataset with lon, lat, i, j coordinates
        to interpolate at

    Returns
    -------
    DataArray
        interpolated data array
        with points dimension
        and passed-through i, j indices
    """
    ida = da.interp(coords=ixds[['lon', 'lat']], method='linear')
    # preserve i,j indices
    for name in ['j', 'i']:
        ida.coords[name] = ixds[name]
    return ida


def lonlat_from_transform(transform, width, height):
    """Make lon, lat arrays from transform and shape"""
    lon, _ = transform * (np.arange(width) + 0.5, np.full(shape=width, fill_value=0.5))
    _, lat = transform * (np.full(shape=height, fill_value=0.5), np.arange(height, 0, -1) - 0.5)
    return lon, lat


def points_to_2d(ds):
    """Map points dataset back to 2D coordinates

    Parameters
    ----------
    ds : Dataset
        dataset with points

    Returns
    -------
    ds
        dataset with lon, lat
    """
    shape = height, width = (ds.attrs['height'], ds.attrs['width'])
    transform = affine.Affine(*ds.attrs['transform'][:6])
    lon, lat = lonlat_from_transform(transform, width=width, height=height)
    coords = dict(lon=lon, lat=lat)

    darrs = {}
    for name, da in ds.data_vars.items():
        data = np.ma.zeros(shape=shape, dtype=da.dtype)
        data[:] = np.ma.masked
        data[ds['j'], ds['i']] = da.values
        darrs[name] = xr.DataArray(data, dims=('lat', 'lon'), name=name)

    dsout = xr.Dataset(darrs, coords=coords)
    dsout['time'] = ds['time']

    return dsout
