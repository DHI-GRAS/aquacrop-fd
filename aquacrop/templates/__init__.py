from pathlib import Path

import numpy as np

DATAFILES = {
    p.name: p for p in Path(__file__).resolve().glob('Climate.*')
}

FREQUENCY_CODES = {
    'daily': 1,
    '10-daily': 2,
    'monthly': 3
}


def _get_frequency(dates):
    """Get frequency in days from list of dates"""
    dd = np.diff(dates)
    frequencies, counts = np.unique([d.total_seconds() for d in dd], return_counts=True)
    frequencies = np.ceil(frequencies / 3600 / 24).astype('int')
    if len(frequencies) == 1:
        frequency = frequencies[0]
    elif counts.max() >= (counts.min() * 10):
        frequency = frequencies[np.argmax(counts)]
    else:
        raise ValueError(
            f'Unable to determine representative frequency. '
            'Found these (with counts): {zip(counts, frequencies)}'
        )
    return frequency


def _get_frequency_code(frequency):
    """Translate frequency in days to frequency code"""
    if frequency == 1:
        return FREQUENCY_CODES['daily']
    elif frequency == 10:
        return FREQUENCY_CODES['10-daily']
    elif frequency in [30, 31]:
        return FREQUENCY_CODES['monthly']
    else:
        raise ValueError(f'No corresponding code found for frequency {frequency}')


def format_aquacrop_data(filename, data, source, outfile):
    """Format AquaCrop input data files"""
    template = DATAFILES[filename].read_text()

    frequency = _get_frequency(data['time'].values)
    frequency_code = _get_frequency_code(frequency)

    data_lines = '\n'.join(f'{value:.4f}' for value in data['data'].values)

    template_filled = template.format(
        source=source,
        start=data['time'].values[0],
        frequency_code=frequency_code,
        data_lines=data_lines
    )
    outfile.write_text(template_filled)
