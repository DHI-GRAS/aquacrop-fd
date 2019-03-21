import contextlib
import logging
import asyncio

import shapely.geometry
import xarray as xr

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

LAND_COVER_CLASS_MAP = {
    'Cropland': 600,
    'Rice': 660
}


def interface(
        plu_path, eto_path, tmp_min_path, tmp_max_path,
        soil_map_path, land_cover_path,
        planting_date, soil, crop, irrigated,
        geometry=None, nproc=None
):

    config = {
        'planting_date': planting_date,
        'crop': crop,
        'soil': soil,
        'irrigated': irrigated
    }

    crop_cycle_length = model_setup.get_crop_cycle_length(crop)

    selkw = {
        'soil_map_path': soil_map_path,
        'land_cover_path': land_cover_path,
        'soil_class': SOIL_CLASS_MAP[soil],
        'land_cover_class': LAND_COVER_CLASS_MAP['Rice' if crop == 'Rice' else 'Cropland'],
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

        data_aligned = climate_in.select_align_inputs(darrs=darrs, **selkw)

        dsout = asyncio.run(run.run_ds(data_aligned, config=config, nproc=nproc))

    logger.info('Map points dataset to 2D raster')
    dsout_latlon = soil_landcover.points_to_2d(dsout)
    return dsout_latlon
