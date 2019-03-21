import os
import itertools
from pathlib import Path
import shutil
import functools
import tempfile
import logging
import concurrent.futures

import xarray as xr
import numpy as np

from aquacrop_fd import model_setup
from aquacrop_fd import execution
from aquacrop_fd import data_out

logger = logging.getLogger(__name__)

MAX_WORKERS = 5
CHUNKSIZES = [5, 20, 35, 50, 65, 75]


def run_single(project_name, rundir, datadir, data_by_name, config):
    executable, listdir = execution.deploy(rundir)
    project_file = model_setup.prepare_data_folder(
        project_name=project_name,
        listdir=listdir,
        datadir=datadir,
        data_by_name=data_by_name,
        config=config
    )
    execution.run(executable, project_file)
    outfiles = execution.get_output_files(rundir, project_name)
    dd = data_out.parse_selected_output(outfiles['day'])
    return dd


def _merge_data_dicts(dds, pointcoord):
    darrs = []
    for name in ['total_irrigation', 'final_yield']:
        data = np.array([df[name] for df in dds])
        da = xr.DataArray(
            data,
            dims=('point'),
            coords=dict(point=pointcoord),
            name=name
        )
        darrs.append(da)
    time = dds[0]['time']
    ds = xr.merge(darrs)
    ds['time'] = [time]
    return ds


def run_ds_chunk(rundir, ds, config):
    rundir = Path(rundir)
    npoints = len(ds.point)
    if npoints > 1000:
        # sanity
        raise ValueError(
            f'Processing {npoints} > 1000 points in one go is a bad idea.'
        )
    elif npoints == 0:
        raise ValueError(f'Empty dataset {ds}')

    executable, listdir = execution.deploy(rundir)

    logger.info(f'Setting up processing of {npoints} points')
    project_names = []
    for k, pt in enumerate(ds['point'].values):
        dspt = ds.sel(point=pt)
        data_by_name = {
            'Climate.PLU': [dspt['PLU'].values],
            'Climate.ETo': [dspt['ETo'].values],
            'Climate.TMP': [dspt[name].values for name in ['TMP_min', 'TMP_max']],
            'time': dspt.time.to_index().to_pydatetime()
        }

        project_name = f'{k:03d}'
        project_names.append(project_name)
        datadir = rundir / f'DATA_{project_name}'

        model_setup.prepare_data_folder(
            project_name=project_name,
            listdir=listdir,
            datadir=datadir,
            data_by_name=data_by_name,
            config=config
        )
    logger.info(list(listdir.glob('*.PRO')))
    timeout = (npoints * 2)
    execution.run(executable, timeout=timeout)

    dds = []
    for project_name in project_names:
        outfiles = execution.get_output_files(rundir, project_name)
        dd = data_out.parse_selected_output(outfiles['day'])
        dds.append(dd)

    ds = _merge_data_dicts(dds, pointcoord=ds['point'])
    return ds


def _chunk_worker(ds, config):
    rundir = Path(tempfile.mkdtemp(prefix='acfd-'))
    try:
        dsout = run_ds_chunk(rundir, ds, config=config)
        # only clean up when run was successful
        try:
            shutil.rmtree(rundir)
        except OSError:
            pass
    except Exception as exc:
        logger.debug(f'Job is failing. Data remains in {rundir}.')
        raise exc

    return dsout


def run_ds(ds, config, nproc=None):
    npoints = len(ds.point)
    chunksizes = itertools.cycle(CHUNKSIZES)
    ntaken = 0
    jobs = []
    while ntaken < npoints:
        chunksize = next(chunksizes)
        ptslice = slice(ntaken, ntaken + chunksize)
        dschunk = ds.isel(point=ptslice)
        if len(dschunk.point) == 0:
            # just in case
            continue
        jobs.append(dschunk)
        ntaken += chunksize

    _worker = functools.partial(_chunk_worker, config=config)

    if nproc is None:
        nproc = os.cpu_count()
    max_workers = min(len(jobs), nproc, MAX_WORKERS)
    logger.info(
        f'Processing {len(jobs)} jobs on {max_workers} workers'
    )
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        all_dsout = executor.map(_worker, jobs)

    logger.info('Merging outputs')
    dsout = xr.merge(all_dsout)
    for name in ['j', 'i']:
        dsout.coords[name] = ds[name]
    dsout.attrs.update(ds.attrs)
    return dsout
