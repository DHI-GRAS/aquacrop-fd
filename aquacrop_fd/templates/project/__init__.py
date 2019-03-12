from pathlib import Path

TEMPLATEFILE = (Path(__file__).parent / 'Template.PRO').resolve()

REQUIRED_PATHS = [
    'Climate.CLI', 'Climate.TMP', 'Climate.ETo',
    'Climate.PLU', 'Climate.CO2', 'Irrigation.IRR',
    'crop', 'soil'
]

REQUIRED_CONFIG = [
    'first_day_sim', 'last_day_sim',
    'first_day_crop', 'last_day_crop'
]


class BlankPath:

    parent = '(None)'
    name = '(None)'


def write_project_file(outfile, paths, config):
    """Format AquaCrop PRO file

    Parameters
    ----------
    outfile : str
        path to output project file
    paths : dict str --> Path
        maps input file keys to paths
    config : dict
        config
    """
    for name in REQUIRED_PATHS:
        if name not in paths:
            paths[name] = BlankPath
            print(f'Setting path {name} to blank')
    #missing_paths = set(REQUIRED_PATHS) - set(paths)
    #if missing_paths:
        #raise ValueError(f'Missing paths for {missing_paths}')

    missing_config = set(REQUIRED_CONFIG) - set(config)
    if missing_config:
        raise ValueError(f'Missing config for {missing_config}')

    fields = dict(paths=paths, **config)
    print(fields)
    template = TEMPLATEFILE.read_text()
    template_formatted = template.format(**fields)
    outfile.write_text(template_formatted)
