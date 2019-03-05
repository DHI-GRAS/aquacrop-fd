import shutil

from aquacrop_fd import templates
from aquacrop_fd.templates import parser
from aquacrop_fd.templates import climate_data

REQUIRED_CLIMATE_FILES = ['Climate.IRR']


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


def write_data_file(filename, outdir, changes, arrs):
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
    climate_data.write_climate_data(lines, arrs)
    dst.write_text('\n'.join(lines))
    return dst


def prepare_data_folder(outdir, ds, crop_type, soil_type, config):
    soil_file = _copy_soil_file(soil_type, outdir)
    crop_file = _copy_crop_file(crop_type, outdir)

    name = 'Climate.IRR'

    if name == 'Climate.IRR':
        changes = {
            'Allowable depletion of RAW (%)': config['Climate.IRR']['fraction']
        }
        arrs = []
