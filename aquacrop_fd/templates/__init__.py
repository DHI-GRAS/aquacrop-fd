from pathlib import Path

HERE = Path(__file__).parent

SUBDIRS = ['climate', 'soil', 'crop']


def _index_folder(path):
    return {p.name: p for p in path.glob('*') if p.suffix not in ['.py', '.pyc']}


DATA = {name: _index_folder(HERE / name) for name in SUBDIRS}
