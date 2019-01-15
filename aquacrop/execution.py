SAMPLE_DATA = {
    'areatype': 'All focus area',
    'areaname': 'Volta',
    'climate': 'Historic',
    'ccscenario': None,
    'forecast': 'ModelBased',
    'crop': 'Maize',
    'soil': 'SandyClayLoam',
    'areaha': 'undefined',
    'planting': '2018-01-01',
    'irregated': False,
    'fraction': 100,
    'id': 0
}


def format_lines(param_sets):
    """Format lines for C# tool
    e.g. areatype=All focus area|areaname=Volta|climate=Forecast|ccscenario=|forecast=ModelBased|
    crop=Maize|soil=SandClayLoam|areaha=undefined|planting=2018-01-01|irrigated=False|fraction=100|id=7

    Parameters
    ----------
    param_sets : list of dict
        list of parameter sets

    Yields
    ------
    str : line to write to file
    """
    for p in param_sets:
        params = []
        for name in SAMPLE_DATA:
            value = p.get(name, None)
            if value is None:
                value = ''
            params.append(f'{name}={value}')
        yield '|'.join(params)
