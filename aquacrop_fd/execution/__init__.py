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
    rundir : str
        run directory

    Returns
    -------
    Path
        path to AquaCrop exe
    """
    with zipfile.ZipFile(EXE_PACKAGE) as zf:
        zf.extractall(rundir)
    return next(Path(rundir).glob('*.exe'))


def run(executable, project_file, timeout=5):
    cmd = ' '.join(map(str, [executable, project_file]))
    logger.debug(f'Running {cmd}')
    print(cmd)
    return subprocess.run(cmd, check=True, timeout=5)
