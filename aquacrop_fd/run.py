import tempfile
from pathlib import Path

from aquacrop_fd import model_setup
from aquacrop_fd import execution


def run_single(project_name, rundir, data, config):
    executable = execution.deploy(rundir)
    project_file = model_setup.prepare_data_folder(
        project_name=project_name,
        outdir=rundir,
        data=data,
        config=config
    )
    execution.run(executable, project_file)


def run_batch(data, config):
    with tempfile.TemporaryDirectory(prefix='acfd_') as tempdir:
        rundir = Path(tempdir)
        run_single(rundir, data, config)
