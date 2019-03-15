import pytest


def test_change_file(climate_file, tmp_path):
    from aquacrop_fd.templates import parser
    outfile = tmp_path / climate_file.name
    parser.change_file(
        infile=climate_file,
        outfile=outfile,
        changes={
            'First day of record (1, 11 or 21 for 10-day or 1 for months)': 99
        },
        raise_missing=True
    )
    assert outfile.is_file()


def test_change_file_fail_missing(climate_file, tmp_path):
    from aquacrop_fd.templates import parser
    outfile = tmp_path / climate_file.name
    with pytest.raises(RuntimeError) as err:
        parser.change_file(
            infile=climate_file,
            outfile=outfile,
            changes={
                'Oh no this will hopefully break': 99
            },
            raise_missing=True
        )
        assert 'not found' in str(err)
