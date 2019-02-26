import pytest

from aquacrop_fd.templates import climate


@pytest.mark.parametrize('filename', list(climate.DATAFILES))
def test_climate_template(filename, data_array_10d, tmp_path):
    from aquacrop_fd import templates
    da = data_array_10d
    arrs = [da.isel(lon=0, lat=0).values]
    outfile = tmp_path / filename
    templates.climate.format_climate_data(
        filename=filename,
        source=da.name,
        outfile=outfile,
        times=da['time'].to_index().to_pydatetime(),
        arrs=arrs
    )
    assert outfile.is_file()
