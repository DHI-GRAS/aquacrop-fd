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


def _get_class_indices(datasets, class_values):
    """Get the indices of points where dataset values match corresponding class values"""
    cond = True
    for src, class_value in zip(datasets, class_values):
        data = src.read(indexes=1)
        cond &= (data == class_value)
    jj, ii = np.where(cond)
    return jj, ii


def find_class_points(paths, class_values, bounds=None):
    """Find points corresponding to class

    Parameters
    ----------
    paths : list of str or Path
        paths to source datasets
    class_values : list of int
        value of class to find for each dataset (path)
    bounds : tuple (xmin, ymin, xmax, ymax), optional
        bounds within file to search
        in lat, lon coordinates

    Yields
    ------
    xr.Dataset
        coordinates of points in current block
        of datasets that are equal to class_values
        together with indices in original image
        (for raster reconstruction)
    """
    if len(paths) != len(class_values):
        raise ValueError('There must be one class value for each dataset.')

    with contextlib.ExitStack() as es:
        datasets = [es.enter_context(rasterio.open(path)) for path in paths]

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

        # take first VRT as model
        vrt = vrts[0]
        jj, ii = _get_class_indices(vrts, class_values=class_values)
        assert np.all(jj < vrt.height)
        assert np.all(ii < vrt.width)

        if len(jj) == 0:
            raise ValueError(
                f'No points found intersecting bounding box and class values {class_values}.'
            )

        # convert pixel indices to lon, lat coordinates
        lon, lat = vrt.transform * (ii, jj)

        # store all in Dataset
        data_vars = {
            name: xr.DataArray(data, dims='point', name=name)
            for name, data in {'lon': lon, 'lat': lat, 'i': ii, 'j': jj}.items()
        }
        ds = xr.Dataset(data_vars, coords={'point': np.arange(len(lon))})
        ds.attrs.update({name: vrt.profile[name] for name in ['width', 'height']})
        # properly serialize transform
        ds.attrs['transform'] = list(vrt.profile['transform'])
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
    selection = ~ida.isnull().all(dim='time')
    ida = ida.isel(point=selection)
    for name in ['j', 'i']:
        ida.coords[name] = ixds[name].isel(point=selection)
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
        data = np.full(shape=shape, fill_value=np.nan, dtype='float')
        data[ds['j'], ds['i']] = da.values
        darrs[name] = xr.DataArray(data, dims=('lat', 'lon'), name=name)

    dsout = xr.Dataset(darrs, coords=coords)
    dsout['time'] = ds['time']

    return dsout
