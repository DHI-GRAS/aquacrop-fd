from pathlib import Path
import json

import click
import dateutil.parser

from aquacrop_fd import interface


class DateType(click.ParamType):
    name = 'date'

    def convert(self, value, param, ctx):
        return dateutil.parser.parse(value)


class GeoJSONFile(click.ParamType):
    name = 'GeoJSON'

    def convert(self, value, param, ctx):
        return json.loads(Path(value).read_text())


class OutdirMakedirs(click.ParamType):
    name = 'outdir'

    def convert(self, value, param, ctx):
        path = Path(value)
        path.mkdir(exist_ok=True, parents=True)
        return path


@click.command()
@click.option(
    '--plu', 'plu_path', required=True,
    help='Path to daily rain input file (pattern)'
)
@click.option(
    '--eto', 'eto_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to monthly mean ETo input file'
)
@click.option(
    '--tmp-min', 'tmp_min_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to monthly mean minimum temperature input file'
)
@click.option(
    '--tmp-max', 'tmp_max_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to monthly mean maximum temperature input file'
)
@click.option(
    '--soil-map', 'soil_map_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to soil map file'
)
@click.option(
    '--land-cover-map', 'land_cover_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to soil map file'
)
@click.option(
    '--planting-date', type=DateType(), required=True,
    help='Planting date'
)
@click.option(
    '--soil', type=click.Choice(list(interface.SOIL_CLASS_MAP)),
    required=True,
    help='Soil class'
)
@click.option(
    '--crop', required=True,
    help='Valid AquaCrop crop name'
)
@click.option(
    '--irrigated/--not-irrigated', required=True,
    help='Whether the soil is irrigated'
)
@click.option(
    '--geometry', type=GeoJSONFile(), required=True,
    help='Path to GeoJSON file with bounds geometry'
)
def run_cli(**kwargs):
    interface(**kwargs)


@click.command()
@click.option(
    '--plu', 'plu_path', required=True,
    help='Path to daily rain input file (pattern)'
)
@click.option(
    '--eto', 'eto_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to monthly mean ETo input file'
)
@click.option(
    '--tmp-min', 'tmp_min_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to monthly mean minimum temperature input file'
)
@click.option(
    '--tmp-max', 'tmp_max_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to monthly mean maximum temperature input file'
)
@click.option(
    '--soil-map', 'soil_map_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to soil map file'
)
@click.option(
    '--land-cover-map', 'land_cover_path', type=click.Path(dir_okay=False, exist=True),
    required=True,
    help='Path to soil map file'
)
@click.option(
    '--outdir', type=OutdirMakedirs(), required=True,
    help='Output directory'
)
@click.option(
    '--api-url', required=True, help='API URL'
)
def run_queues(**kwargs):
    pass
