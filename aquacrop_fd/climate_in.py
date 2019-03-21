import logging

import xarray as xr
import pandas as pd

from aquacrop_fd import soil_landcover
from aquacrop_fd import time_resampling

logger = logging.getLogger(__name__)

DARR_NAMES = ['PLU', 'ETo', 'TMP_min', 'TMP_max']
DARR_NAMES_DAILY = ['PLU']


def remove_empty_points(ds):
    """Remove points where at least one of the variables is all NaN"""
    all_nodata = ds.count(dim='time') == 0
    bad = False
    for da in all_nodata.data_vars.values():
        bad |= da
    if bad.any():
        dssel = ds.isel(point=~bad)
        dssel.attrs.update(ds.attrs)
        return dssel
    else:
        return ds


def select_align_inputs(
        darrs,
        soil_map_path, land_cover_path, soil_class, land_cover_class,
        start, end, bounds=None
):
    """Select and align input data

    Parameters
    ----------
    darrs : dict str --> xr.DataArray
        mapping DARR_NAMES to data arrays
    soil_map_path, land_cover_path : str
        path to soil map and land cover map files
        (files must be pixel-perfectly aligned)
    soil_class, land_cover_class : int
        classes from each file to select
    start, end : datetime.datetime
        time range
    bounds : tuple, optional
        xmin, ymin, xmax, ymax

    Returns
    -------
    xr.Dataset
        dataset with time- and space-aligned
        variables for all DARR_NAMES
    """
    missing = set(DARR_NAMES) - set(darrs)
    if missing:
        raise ValueError(f'Missing the following data arrays in darrs: {missing}')

    # find pixels
    logger.info('Finding points matching selected classes')
    ixds = soil_landcover.find_class_points(
        paths=[soil_map_path, land_cover_path],
        class_values=[soil_class, land_cover_class],
        bounds=bounds
    )
    logger.info(f'Found {len(ixds.point)} points')
    logger.info(f'Index specs are {ixds.attrs}')

    # interpolate in space
    darrs_pt = {}
    for name in DARR_NAMES:
        logger.info(f'Space-interpolating {name} at land cover points')
        da = darrs[name]
        da = soil_landcover.interpolate_to_points(da, ixds)
        darrs_pt[name] = da

    # interpolate in time to have complete and aligned time series
    time_index = pd.date_range(start=start, end=end, freq='1D')
    darrs_pt_time = {}
    for name in DARR_NAMES:
        da = darrs_pt[name]
        if name in DARR_NAMES_DAILY:
            # data is already daily
            # just select
            logger.info(f'Time=indexing daily {name}')
            da = da.sel(time=time_index)
        else:
            # resample to same daily index
            logger.info(f'Time-interpolating {name} to daily values')
            da = time_resampling.resample_means(da, time_index)
        da.name = name
        darrs_pt_time[name] = da

    logger.info('Merging variables into one dataset')
    ds = xr.merge(darrs_pt_time.values())
    ds.attrs.update(ixds.attrs)
    return remove_empty_points(ds)
