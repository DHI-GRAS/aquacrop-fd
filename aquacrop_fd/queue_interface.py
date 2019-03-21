from pathlib import Path
import logging

import requests

from aquacrop_fd import interface
from aquacrop_fd import queue_schemas
from aquacrop_fd.scripts import netcdf_output

logger = logging.getLogger(__name__)


def get_job(api_url):
    url = api_url + '/getjob'
    r = requests.post(url, json={'num_messages': 1})
    if not r.ok:
        if 'No message found' in r.text:
            return None
        else:
            raise RuntimeError(
                f'Request failed with message {r.text}'
            )
    job_raw = r.json()
    logger.info(f'Processing job {job_raw}')
    schema = queue_schemas.JobSchema()
    return schema.load(job_raw)


def put_done(api_url, guid, error):
    url = api_url + '/getjob'
    r = requests.post(url, json={'guid': guid, 'error': error or ''})
    r.raise_for_status()


def work_queue(
        api_url,
        plu_path, eto_path, tmp_min_path, tmp_max_path,
        soil_map_path, land_cover_path,
        outdir
):
    if not api_url.endswith('/'):
        api_url = api_url + '/'

    while True:
        logger.info('Attempting to get job from queue')
        job = get_job(api_url)
        if job is None:
            logger.info('No more jobs to process.')
            break

        guid = job['guid']

        error_message = None
        try:
            ds = interface(
                plu_path=plu_path, eto_path=eto_path,
                tmp_min_path=tmp_min_path, tmp_max_path=tmp_max_path,
                soil_map_path=soil_map_path, land_cover_path=land_cover_path,
                **job
            )
            outfile = Path(outdir) / f'{guid}.nc'
            logger.info(f'Writing result to {outfile}')
            netcdf_output.to_netcdf(ds, outfile)

        except (RuntimeError, ValueError, TypeError) as error:
            logger.exception(f'Job {guid} failed!')
            error_message = f'Processing failed. ({str(error)})'

        put_done(api_url, guid=guid, error=error_message)
