from pathlib import Path

TEMPLATEFILE = (Path(__file__).parent / 'Template.PRO').resolve()

REQUIRED_PATHS = [
    'Climate.CLI', 'Climate.TMP', 'Climate.Eto',
    'Climate.Plu', 'Climate.CO2', 'Climate.IRR',
    'crop', 'soil'
]

REQUIRED_CONFIG = [
    'first_day_sim', 'last_day_sim',
    'first_day_crop', 'last_day_crop'
]


def write_project_file(outfile, paths, config):
    """Format AquaCrop PRO file

    Parameters
    ----------
    paths : dict str --> Path
        maps input file keys to paths


    """

    missing_paths = set(REQUIRED_PATHS) - set(paths)
    if missing_paths:
        raise ValueError(f'Missing paths for {missing_paths}')

    missing_config = set(REQUIRED_CONFIG) - set(config)
    if missing_config:
        raise ValueError(f'Missing config for {missing_config}')

    fields = dict(paths=paths, **config)
    template = TEMPLATEFILE.read_text()
    template_formatted = template.format(**fields)
    outfile.write_text(template_formatted)
