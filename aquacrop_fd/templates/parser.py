import re
from pathlib import Path


def _split_line(line):
    ww = re.split(':', line, maxsplit=1)
    if len(ww) == 2:
        return [s.strip() for s in ww]
    else:
        return None, None


def _format_value(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, float):
        return f'{value:.3f}'
    else:
        return str(value)


def _join_line(value, name, linelen=None):
    value_str = _format_value(value)
    if linelen is not None:
        nwhite = max(
            (linelen - len(name) - 5 - len(value_str) + 1),
            1
        )
    else:
        nwhite = 1
    return (' ' * nwhite + value_str + '  :  ' + name)


def parse_file(path):
    lines = path.read_text()
    properties = {}
    for line in lines.splitlines():
        value, name = _split_line(line)
        if name is None:
            continue
        else:
            properties[name] = value
    return properties


def change_lines(lines, changes, raise_missing=True):
    """Loop through lines and apply changes

    Parameters
    ----------
    lines : list of str
        lines in file
    changes : dict str --> str
        line names mapped to values
    raise_missing : bool
        check and raise for missing values

    Returns
    -------
    list of str
        changed lines
    """
    changed = []
    lines_out = []
    for line in lines:
        value, name = _split_line(line)
        if name in changes:
            newvalue = changes[name]
            lines_out.append(
                _join_line(
                    value=newvalue,
                    name=name,
                    linelen=len(line))
            )
            changed.append(name)
        else:
            lines_out.append(line)

    if raise_missing:
        missing = set(changes) - set(changed)
        if missing:
            raise RuntimeError(
                'Some changes were not applied because the '
                f'lines were not found: {missing}'
            )
    return lines_out


def change_file(infile, outfile, changes, raise_missing=True):
    """Change an AquaCrop config file

    Parameters
    ----------
    infile, outfile : str or Path
        paths to input and output files
    changes : dict str --> str
        line names mapped to values
    raise_missing : bool
        check and raise for missing values
    """
    infile, outfile = map(Path, [infile, outfile])
    lines = infile.read_text().splitlines()
    try:
        lines_out = change_lines(lines, changes, raise_missing=raise_missing)
    except RuntimeError as err:
        raise RuntimeError(f'Error changing {infile.name}: {err}')
    outfile.write_text('\n'.join(lines_out))
