from pathlib import Path
import logging

import requests

from aquacrop_fd import interface
from aquacrop_fd import queue_schemas
from aquacrop_fd.scripts import netcdf_output

logger = logging.getLogger(__name__)


def get_job(api_url):
    logger.info('Attempting to get job from queue')
    url = api_url + '/getjob'
    r = requests.post(url, json={'num_messages': 1})
    if not r.ok:
        if 'No message found' in r.text:
            return None
        else:
            logger.info(f'Getting JOB message failed: {r.text}')
            raise RuntimeError(
                f'Request failed with message {r.text}'
            )
    job_raw = r.json()
    job_raw['geometry']['type'] = 'Polygon'
    logger.info(f'Processing job {job_raw}')
    schema = queue_schemas.JobSchema()
    return schema.load(job_raw)


def put_done(api_url, guid, error):
    url = api_url + '/putdone'
    schema = queue_schemas.DoneSchema()
    data = schema.dump({'guid': guid, 'error': error or None})
    r = requests.post(url, json=data)
    if not r.ok:
        logger.info(f'Putting DONE message failed: {r.text}')
    r.raise_for_status()


def write_job_file(dirpath, job, failed=False):
    failedstr = '-failed' if failed else ''
    outfile = Path(dirpath) / '{guid}{failedstr}.json'.format(failedstr=failedstr, **job)
    logger.info(f'Writing jobs file to {outfile}')
    schema = queue_schemas.JobSchema()
    outfile.write_text(schema.dumps(job, indent=2))


def _get_jobs_getter(job_files):
    """Terrible hack to fork between jobs from files and jobs from queues"""
    global get_job
    if job_files is not None and job_files:
        # hack to bypass jobs queue communication
        _job_file_iter = iter(job_files)

        def read_jobs(*args, **kwargs):
            try:
                path = Path(next(_job_file_iter))
            except StopIteration:
                return None
            schema = queue_schemas.JobSchema()
            return schema.loads(path.read_text())

        return read_jobs
    else:
        return get_job


def work_queue(
        api_url,
        plu_path, eto_path, tmp_min_path, tmp_max_path,
        soil_map_path, land_cover_path,
        outdir, job_file_dir=None,
        job_files=None
):
    if not api_url.endswith('/'):
        api_url = api_url + '/'

    # fork between queue and file jobs
    jobs_getter = _get_jobs_getter(job_files)

    while True:
        job = jobs_getter(api_url)
        if job is None:
            logger.info('No more jobs to process.')
            break

        if job_file_dir is not None:
            write_job_file(job_file_dir, job)

        guid = job['guid']
        logger.info(f'Processing job {guid}')

        kw = {
            k: job[k] for k in
            ['planting_date', 'crop', 'irrigated', 'fraction', 'geometry']
        }

        error_message = None
        try:
            ds = interface.interface(
                plu_path=plu_path, eto_path=eto_path,
                tmp_min_path=tmp_min_path, tmp_max_path=tmp_max_path,
                soil_map_path=soil_map_path, land_cover_path=land_cover_path,
                **kw
            )
            outfile = Path(outdir) / f'{guid}.nc'
            logger.info(f'Writing result to {outfile}')
            netcdf_output.to_netcdf(ds, outfile)
        except Exception as error:
            logger.exception(f'Job {guid} failed!')
            error_message = f'Processing failed. ({str(error)})'
            if job_file_dir is not None:
                write_job_file(job_file_dir, job, failed=True)
            raise
        finally:
            logger.info('Putting DONE message')
            put_done(api_url, guid=guid, error=error_message)
