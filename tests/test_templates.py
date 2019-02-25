import pytest

CLIMATE_FILENAMES = ['Climate.ETo', 'Climate.PLU', 'Climate.TMP']


@pytest.mark.parametrize('filename', CLIMATE_FILENAMES)
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
