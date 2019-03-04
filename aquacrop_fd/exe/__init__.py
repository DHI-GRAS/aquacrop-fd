import zipfile
from pathlib import Path


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
    with zipfile.ZipFile() as zf:
        zf.extractall(rundir)
    return next(Path(rundir).glob('*.exe'))
