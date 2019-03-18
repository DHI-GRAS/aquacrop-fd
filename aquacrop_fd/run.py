import tempfile
from pathlib import Path

from aquacrop_fd import model_setup
from aquacrop_fd import execution


def run_single(project_name, rundir, datadir, data_by_name, config):
    executable, listdir = execution.deploy(rundir)
    project_file = model_setup.prepare_data_folder(
        project_name=project_name,
        rundir=rundir,
        datadir=datadir,
        data_by_name=data_by_name,
        config=config
    )
    execution.run(executable, project_file)


def run_batch(data2d, config):
    with tempfile.TemporaryDirectory(prefix='acfd_') as tempdir:
        rundir = Path(tempdir)
        datadir = rundir / '{}'
        run_single(
            project_name=project_name,
            rundir=rundir,
            datadir=datadir,
            data_by_name=data_by_name,
            config=config
        )
