import pytest

from aquacrop_fd.templates import climate


@pytest.mark.parametrize('filename', list(climate.DATAFILES))
def test_climate_template(filename, data_array, tmp_path):
    from aquacrop_fd import templates
    da = data_array
    outfile = tmp_path / filename
    templates.climate.format_climate_data(
        filename=filename,
        source=da.name,
        outfile=outfile,
        darrs=[da]
    )
    assert outfile.is_file()
