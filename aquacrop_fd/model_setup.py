import shutil
import datetime
import logging

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


def _copy_soil_file(soil, outdir):
    filename = soil + '.SOL'
    soils = templates.DATA['soil']
    try:
        src = soils[filename]
    except KeyError:
        raise ValueError(
            f'Soil file {filename} not found. Choose from {list(soils)}.'
        )
    dst = outdir / filename
    shutil.copy(src, dst)
    return dst


def _copy_crop_file(crop, outdir):
    # first letter capital
    filename = crop + '.CRO'
    crops = templates.DATA['crop']
    try:
        src = crops[filename]
    except KeyError:
        raise ValueError(
            f'Soil file {filename} not found. Choose from {list(crops)}.'
        )
    dst = outdir / filename
    shutil.copy(src, dst)
    return dst


def _get_crop_cycle_length(crop_file):
    data = parser.parse_file(crop_file)
    try:
        daystr = data["Calendar Days: from sowing to maturity (length of crop cycle)"]
    except KeyError:
        raise KeyError(f'length of crop cycle not found in crop file {crop_file}')
    return datetime.timedelta(days=int(daystr))


def write_climate_file(filename, outdir, arrs, times, changes=None):

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
    dst = outdir / filename
    lines = src.read_text().splitlines()
    try:
        lines = climate_data.write_climate_data(lines, arrs, times=times, extra_changes=changes)
    except RuntimeError as err:
        raise RuntimeError(f'Error changing {filename}: {err!s}') from err
    dst.write_text('\n'.join(lines))
    return dst


def copy_climate_file(outdir, filename):
    src = templates.DATA['climate'][filename]
    dst = outdir / src.name
    shutil.copy(src, dst)
    return dst


def write_net_irrigation_file(outdir, fraction):
    infile = templates.DATA['climate']['Irrigation.IRR']
    outfile = outdir / infile.name
    changes = {
        'Allowable depletion of RAW (%)': fraction
    }
    parser.change_file(infile, outfile, changes)
    return outfile


def prepare_data_folder(outdir, data, config):

    datadir = outdir / 'DATA'
    listdir = outdir / 'LIST'
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
    crop_cycle_length = _get_crop_cycle_length(paths['crop'])
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
    irrpath = write_net_irrigation_file(datadir, fraction=config.get('fraction', 100))
    paths[irrpath.name] = irrpath

    # write climate files
    for filename in REQUIRED_CLIMATE_FILES:
        logger.debug(f'Writing data for {filename}')
        paths[filename] = write_climate_file(
            filename=filename,
            outdir=datadir,
            arrs=data[filename]['arrs'],
            times=data[filename]['times']
        )

    # write CO2 file
    for filename in STATIC_CLIMATE_FILES:
        paths[filename] = copy_climate_file(datadir, filename)

    # write project file
    project_file = listdir / 'project.PRO'
    project.write_project_file(
        outfile=project_file,
        paths=paths,
        config=project_config
    )

    return project_file
