from pathlib import Path
import datetime
import json
import logging

import click
import dateutil.parser

from aquacrop_fd import interface

logger = logging.getLogger(__name__)


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


def setup_logging(debug=False, log_dir=None):
    level = 'DEBUG' if debug else 'INFO'
    logger = logging.getLogger('aquacrop_fd')
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch_fmt = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    ch.setFormatter(ch_fmt)
    logger.addHandler(ch)

    logfile = None
    if log_dir is not None:
        now = datetime.datetime.now()
        logfname = f'{now:%Y%m%d}-{now:%H%M%S}.log'
        logfile = Path(log_dir) / logfname
        fh = logging.FileHandler(logfile)
        fh.setLevel(level)
        fh_fmt = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        fh.setFormatter(fh_fmt)
        logger.addHandler(fh)
    return logfile


@click.command()
@click.option(
    '--plu', 'plu_path', required=True,
    help='Path to daily rain input file (pattern)'
)
@click.option(
    '--eto', 'eto_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to monthly mean ETo input file'
)
@click.option(
    '--tmp-min', 'tmp_min_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to monthly mean minimum temperature input file'
)
@click.option(
    '--tmp-max', 'tmp_max_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to monthly mean maximum temperature input file'
)
@click.option(
    '--soil-map', 'soil_map_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to soil map file'
)
@click.option(
    '--land-cover-map', 'land_cover_path', type=click.Path(dir_okay=False, exists=True),
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
@click.option(
    '--log-dir', type=OutdirMakedirs(), default=None,
    help='Write log files and job files to this directory'
)
def run_cli(log_dir, **kwargs):
    setup_logging(log_dir=log_dir)
    interface.interface(**kwargs)


@click.command()
@click.option(
    '--plu', 'plu_path', required=True,
    help='Path to daily rain input file (pattern)'
)
@click.option(
    '--eto', 'eto_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to monthly mean ETo input file'
)
@click.option(
    '--tmp-min', 'tmp_min_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to monthly mean minimum temperature input file'
)
@click.option(
    '--tmp-max', 'tmp_max_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to monthly mean maximum temperature input file'
)
@click.option(
    '--soil-map', 'soil_map_path', type=click.Path(dir_okay=False, exists=True),
    required=True,
    help='Path to soil map file'
)
@click.option(
    '--land-cover-map', 'land_cover_path', type=click.Path(dir_okay=False, exists=True),
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
@click.argument(
    'job_files', type=click.Path(dir_okay=False, exists=True), nargs=-1,
    default=None
)
@click.option(
    '--log-dir', type=OutdirMakedirs(), default=None,
    help='Write log files and job files to this directory'
)
@click.option(
    '--delete-no-op-logs/--keep-no-op-logs', default=True, show_default=True,
    help='Delete log files when no real work was done'
)
def run_queues(log_dir, delete_no_op_logs=False, **kwargs):
    logfile = setup_logging(log_dir=log_dir)
    work_done = None
    try:
        from aquacrop_fd import queue_interface
        job_file_dir = Path(log_dir) / 'job-files'
        job_file_dir.mkdir(parents=True, exist_ok=True)
        kwargs['job_file_dir'] = job_file_dir
        kwargs['log_file_dir'] = job_file_dir
        work_done = queue_interface.work_queue(**kwargs)
    except queue_interface.JobFailure:
        # all under control
        pass
    except Exception as error:
        logger.critical(f'Unexpected error: {error}')
        raise error
    finally:
        if delete_no_op_logs and not work_done and logfile is not None:
            try:
                logfile.unlink()
            except OSError:
                pass
