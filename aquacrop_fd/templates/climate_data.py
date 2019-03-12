import logging
import datetime

import numpy as np

from aquacrop_fd.templates import parser

logger = logging.getLogger(__name__)

FREQUENCY_CODES = {
    'daily': 1,
    '10-daily': 2,
    'monthly': 3
}

START_DATE_BLANK = datetime.datetime(1901, 1, 1)


def _get_frequency(dates):
    """Get frequency in days from list of dates"""
    dd = np.diff(dates)
    frequencies, counts = np.unique([d.total_seconds() for d in dd], return_counts=True)
    frequencies = np.ceil(frequencies / 3600 / 24).astype('int')
    if len(frequencies) == 1:
        frequency = frequencies[0]
    elif counts.max() >= (counts[counts != counts.max()].max() * 10):
        # most frequent is 10x more common than second-most frequent
        frequency = frequencies[np.argmax(counts)]
    else:
        raise ValueError(
            f'Unable to determine representative frequency. '
            f'Found these (with counts): {list(zip(counts, frequencies))}'
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


def _format_climate_data(arrs, times=None):
    """Format AquaCrop input data files"""
    # check shapes
    if (len(set(np.shape(a) for a in arrs)) > 1) or (np.ndim(arrs[0]) != 1):
        raise ValueError(
            'Data arrays must all be 1D and same length'
        )
    # get frequency code and start date
    if times is not None:
        frequency = _get_frequency(times)
        timekw = dict(
            frequency_code=_get_frequency_code(frequency),
            start=times[0]
        )
    else:
        timekw = dict(
            frequency_code=_get_frequency_code(1),
            start=START_DATE_BLANK
        )
    # format data lines
    data_lines = [
        '    '.join(f'{value:.4f}' for value in values)
        for values in zip(*arrs)
    ]
    return timekw, data_lines


def _find_break(lines):
    positions = []
    for i, line in enumerate(lines):
        if '====' in line:
            positions.append(i)
    if not positions:
        raise ValueError(f'Unable to find data separator in lines {lines}')
    elif len(positions) > 1:
        raise ValueError(f'Found more than one separator in lines {lines}')
    else:
        return positions[0]


def _write_climate_lines(lines, data_lines):
    pos = _find_break(lines)
    lines_out = lines[:(pos + 1)]
    lines_out += data_lines
    return lines_out


def _format_changes(frequency_code, start):
    return {
        'Daily records (1=daily, 2=10-daily and 3=monthly data)': frequency_code,
        'First day of record (1, 11 or 21 for 10-day or 1 for months)': f'{start.day}',
        'First month of record': f'{start.month}',
        'First year of record (1901 if not linked to a specific year)': f'{start.year}'
    }


def write_climate_data(lines, arrs, times=None, extra_changes=None):
    timekw, data_lines = _format_climate_data(arrs=arrs, times=times)
    changes = _format_changes(**timekw)
    if extra_changes is not None:
        changes.update(extra_changes)
    logger.debug(f'Climate data changes: {changes}')
    # write config
    lines = parser.change_lines(lines, changes=changes)
    # write data
    lines = _write_climate_lines(lines, data_lines)
    return lines
