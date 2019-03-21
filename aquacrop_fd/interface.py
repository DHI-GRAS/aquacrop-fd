import contextlib
import logging

import shapely.geometry
import xarray as xr
import numpy as np

from aquacrop_fd import climate_in
from aquacrop_fd import run
from aquacrop_fd import model_setup
from aquacrop_fd import soil_landcover

logger = logging.getLogger(__name__)

SOIL_CLASS_MAP = {
    'Clay': 1,
    'ClayLoam': 2,
    'LoamySand': 3,
    'Sand': 4,
    'SandyClay': 5,
    'SandyLoam': 6,
    'Silt': 7,
    'SiltClayLoam': 8,
    'SiltLoam': 9,
    'SiltyClay': 10
}

SOIL_CLASS_MAP_REVERSED = {value: name for name, value in SOIL_CLASS_MAP.items()}

LAND_COVER_CLASS_MAP = {
    'Cropland': 600,
    'Rice': 660
}


def _soil_class_values_to_names(ds):
    smr = np.array(list(SOIL_CLASS_MAP_REVERSED.values()))
    da = ds['soil_class']
    return ds.assign(
        {'soil_class_name': xr.DataArray(smr[da.values], dims=da.dims, coords=da.coords)}
    )


def interface(
        plu_path, eto_path, tmp_min_path, tmp_max_path,
        soil_map_path, land_cover_path,
        planting_date, crop, irrigated, fraction,
        geometry=None, nproc=None
):

    config = {
        'planting_date': planting_date,
        'crop': crop,
        'fraction': fraction,
        'irrigated': irrigated
    }

    crop_cycle_length = model_setup.get_crop_cycle_length(crop)
    land_cover_class_name = 'Rice' if crop == 'Rice' else 'Cropland'
    land_cover_class = LAND_COVER_CLASS_MAP[land_cover_class_name]

    selkw = {
        'soil_map_path': soil_map_path,
        'land_cover_path': land_cover_path,
        'land_cover_class': land_cover_class,
        'start': planting_date,
        'end': planting_date + crop_cycle_length
    }
    logger.info('Time window is {start:%Y-%m-%d} {end:%Y-%m-%d}'.format(**selkw))

    if geometry is not None:
        geom = shapely.geometry.shape(geometry)
        selkw['bounds'] = geom.bounds

    with contextlib.ExitStack() as es:
        # open all climate data files
        darrs = {}
        logger.info('Opening all input data')
        for key, path in zip(
                ['PLU', 'ETo', 'TMP_min', 'TMP_max'],
                [plu_path, eto_path, tmp_min_path, tmp_max_path]
        ):
            ds = es.enter_context(xr.open_mfdataset(path))
            if len(ds.data_vars) != 1:
                raise ValueError(
                    f'Expecting datasets with one data variable. Got {ds}.'
                )
            da = next(iter(ds.data_vars.values()))
            darrs[key] = da

        # align inputs in time and space
        data_aligned = climate_in.select_align_inputs(darrs=darrs, **selkw)

    # add variable with soil class name
    data_aligned = _soil_class_values_to_names(data_aligned)

    # run AquaCrop
    dsout = run.run_ds(data_aligned, config=config, nproc=nproc)

    # return this information also
    dsout = dsout.assign({'soil_class_name': data_aligned['soil_class_name']})

    # map points back to 2D grid
    logger.info('Map points dataset to 2D raster')
    dsout_latlon = soil_landcover.points_to_2d(dsout)
    return dsout_latlon
