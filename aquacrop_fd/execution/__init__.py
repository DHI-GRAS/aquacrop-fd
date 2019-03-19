import zipfile
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

EXE_PACKAGE = Path(__file__).parent / 'ACsaV60Nr17042017.zip'


def deploy(rundir):
    """Unpack executable to rundir

    Parameters
    ----------
    rundir : Path
        run directory

    Returns
    -------
    Path
        path to AquaCrop exe
    """
    with zipfile.ZipFile(EXE_PACKAGE) as zf:
        zf.extractall(rundir)
    exe = next(Path(rundir).glob('*.exe'))
    listdir = Path(rundir) / 'LIST'
    if not listdir.is_dir():
        raise RuntimeError(f'Something went wrong creating LIST dir in {listdir}')
    return exe, listdir


def run(executable, project_file, timeout=5):
    cmd = ' '.join(map(str, [executable, project_file]))
    logger.debug(f'Running {cmd}')
    print(cmd)
    return subprocess.run(cmd, check=True, timeout=5)


def get_output_files(rundir, project_name):

    outdir = rundir / 'OUTP'

    names = {key: f'{project_name}PRO{key}.OUT' for key in ['day', 'season']}

    paths = {}
    for key, name in names.items():
        path = outdir / name
        if not path.is_file():
            raise RuntimeError(f'Output file not found in {path}.')
        paths[key] = path

    return paths
