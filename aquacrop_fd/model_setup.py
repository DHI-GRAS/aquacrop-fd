import shutil
import datetime
import logging
import asyncio

import aiofiles

from aquacrop_fd import utils
from aquacrop_fd import templates
from aquacrop_fd.templates import parser
from aquacrop_fd.templates import climate_data
from aquacrop_fd.templates import project

logger = logging.getLogger(__name__)

REQUIRED_CLIMATE_FILES = ['Climate.TMP', 'Climate.ETo', 'Climate.PLU']

STATIC_CLIMATE_FILES = ['Climate.CLI', 'Climate.CO2']

REQUIRED_AUX_FILES = ['Irrigation.IRR']

REQUIRED_CONFIG = ['soil', 'crop', 'planting_date']

CLIMATE_NCOLS = {
    'Climate.TMP': 2,
    'Climate.ETo': 1,
    'Climate.PLU': 1
}


def _copy_soil_file(soil, datadir):
    filename = soil + '.SOL'
    soils = templates.DATA['soil']
    try:
        src = soils[filename]
    except KeyError:
        raise ValueError(
            f'Soil file {filename} not found. Choose from {list(soils)}.'
        )
    dst = datadir / filename
    shutil.copy(src, dst)
    return dst


def _find_crop_file(crop):
    filename = crop + '.CRO'
    crops = templates.DATA['crop']
    try:
        return crops[filename]
    except KeyError:
        raise ValueError(
            f'Crop file {filename} not found. Choose from {list(crops)}.'
        )


def _copy_crop_file(crop, datadir):
    filename = crop + '.CRO'
    src = _find_crop_file(crop)
    dst = datadir / filename
    shutil.copy(src, dst)
    return dst


async def _get_crop_cycle_length(crop_file):
    data = await parser.parse_file(crop_file)
    try:
        daystr = data["Calendar Days: from sowing to maturity (length of crop cycle)"]
    except KeyError:
        raise KeyError(f'length of crop cycle not found in crop file {crop_file}')
    return datetime.timedelta(days=int(daystr))


async def write_climate_file(filename, datadir, arrs, time, changes=None):
    """Write climate file

    Parameters
    ----------
    filename : str
        template file name
    datadir : Path
        directory to write to
    arrs : list of 1D arrays
        data to write to columns
    time : 1D array of datetime.datetime
        time
    changes : dict, optional
        additional changes to apply to template file

    Returns
    -------
    Path
        path to created data file
    """
    ncols = CLIMATE_NCOLS.get(filename, None)
    if ncols is not None and len(arrs) != ncols:
        raise ValueError(f'Climate file {filename} requires {ncols} columns. Got {len(arrs)}.')

    climate_templates = templates.DATA['climate']
    try:
        src = climate_templates[filename]
    except KeyError as err:
        raise ValueError(
            f'Climate file {filename} not found. Choose from {list(climate_templates)}'
        ) from err
    dst = datadir / filename
    async with aiofiles.open(str(src)) as f:
        lines = await f.read()

    lines = lines.splitlines()
    try:
        lines = climate_data.write_climate_data(lines, arrs, time=time, extra_changes=changes)
    except RuntimeError as err:
        raise RuntimeError(f'Error changing {filename}: {err!s}') from err

    async with aiofiles.open(str(dst), mode='w') as f:
        await f.write('\n'.join(lines))
    return dst


def copy_climate_file(datadir, filename):
    src = templates.DATA['climate'][filename]
    dst = datadir / src.name
    shutil.copy(src, dst)
    return dst


async def write_net_irrigation_file(datadir, fraction):
    infile = templates.DATA['climate']['Irrigation.IRR']
    outfile = datadir / infile.name
    changes = {
        'Allowable depletion of RAW (%)': fraction
    }
    await parser.change_file(infile, outfile, changes)
    return outfile


def get_crop_cycle_length(crop):
    """Get crop cycle length for named crop"""
    path = _find_crop_file(crop)
    return asyncio.run(_get_crop_cycle_length(path))


async def prepare_data_folder(project_name, listdir, datadir, data_by_name, config):
    """Write all data, aux, and config files into project directory

    Parameters
    ----------
    project_name : str
        project name, will be used in PRO file name
    listdir : Path
        path to store project file in
    datadir : Path
        path to store data files in
    data_by_name : dict
        maps data file names to 1D arrays
        must include `time`, too.
    config : dict
        config with REQUIRED_CONFIG

    Returns
    -------
    Path
        path to {project_name}.PRO
    dict
        project config
    """
    for path in [datadir, listdir]:
        path.mkdir(parents=True, exist_ok=True)

    paths = {}

    missing_config = set(REQUIRED_CONFIG) - set(config)
    if missing_config:
        raise ValueError(f'Config is missing information: {missing_config}')

    # write soil and crop files
    paths['soil'] = _copy_soil_file(config['soil'], datadir)
    paths['crop'] = _copy_crop_file(config['crop'], datadir)

    # calculate date range for crop type
    crop_cycle_length = await _get_crop_cycle_length(paths['crop'])
    start_date = config['planting_date']
    end_date = start_date + crop_cycle_length
    project_config = {
        'first_day_crop': utils.date_to_num(start_date),
        'first_day_sim': utils.date_to_num(start_date),
        'last_day_crop': utils.date_to_num(end_date),
        'last_day_sim': utils.date_to_num(end_date)
    }
    logger.debug(f'Project config is: {project_config}')

    # write irrigation file
    if config.get('irrigated', False):
        irrpath = await write_net_irrigation_file(datadir, fraction=config.get('fraction', 100))
        paths[irrpath.name] = irrpath

    # write climate files
    for filename in REQUIRED_CLIMATE_FILES:
        logger.debug(f'Writing data for {filename}')
        paths[filename] = await write_climate_file(
            filename=filename,
            datadir=datadir,
            arrs=data_by_name[filename],
            time=data_by_name['time']
        )

    # write CO2 file
    for filename in STATIC_CLIMATE_FILES:
        paths[filename] = copy_climate_file(datadir, filename)

    # write project file
    project_file = listdir / f'{project_name}.PRO'
    await project.write_project_file(
        outfile=project_file,
        paths=paths,
        config=project_config
    )

    return project_file, project_config
