import shutil
import datetime
import logging

from aquacrop_fd import utils
from aquacrop_fd import templates
from aquacrop_fd.templates import parser
from aquacrop_fd.templates import climate_data

logger = logging.getLogger(__name__)

REQUIRED_CLIMATE_FILES = ['Climate.IRR', 'Climate.TMP', 'Climate.Eto', 'Climate.CO2']


def _copy_soil_file(soil_type, outdir):
    filename = soil_type.capitalize() + '.SOL'
    soils = templates.DATA['soil']
    try:
        src = soils[filename]
    except KeyError:
        raise ValueError(
            f'Soil type {soil_type} not found. Choose from {list(soils)}.'
        )
    dst = outdir / filename
    shutil.copy(src, dst)
    return dst


def _copy_crop_file(crop_type, outdir):
    filename = crop_type.capitalize() + '.CRO'
    crops = templates.DATA['crop']
    try:
        src = crops[filename]
    except KeyError:
        raise ValueError(
            f'Soil type {crop_type} not found. Choose from {list(crops)}.'
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


def write_data_file(filename, changes, arrs, times, outdir):
    try:
        src = templates.DATA['climate'][filename]
    except KeyError:
        raise ValueError(
            f'Climate file {filename} not found.'
        )
    dst = outdir / filename
    lines = src.read_text().splitlines()
    if changes:
        lines = parser.change_lines(lines, changes=changes)
    climate_data.write_climate_data(lines, arrs, times=times)
    dst.write_text('\n'.join(lines))
    return dst


def prepare_data_folder(outdir, ds, crop_type, soil_type, config):
    paths = {}

    paths['soil'] = _copy_soil_file(soil_type, outdir)
    paths['crop'] = _copy_crop_file(crop_type, outdir)

    crop_cycle_length = _get_crop_cycle_length(paths['crop'])

    start_date = config['planting_date']
    end_date = start_date = crop_cycle_length
    project_config = {
        'first_day_crop': utils.date_to_num(start_date),
        'first_day_sim': utils.date_to_num(start_date),
        'last_day_crop': utils.date_to_num(end_date),
        'last_day_sim': utils.date_to_num(end_date)
    }
    logger.debug(f'Project config is: {project_config}')

    for filename in REQUIRED_CLIMATE_FILES:
        changes = {}

        if filename == 'Climate.IRR':
            changes.update({
                'Allowable depletion of RAW (%)': config['Climate.IRR']['fraction']
            })

        paths[filename] = write_data_file(
            filename=filename,
            changes=changes,
            arrs=arrs,
            times=times,
            outdir=outdir
        )

    project_file = outdir / 'project.PRO'
    templates.project.write_project_file(
        outfile=project_file,
        paths=paths,
        config=project_config
    )

    return paths
