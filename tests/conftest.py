import pytest

import datagen


@pytest.fixture
def data_array():
    return datagen.create_data_array()


def data_file(data_array, tmp_path_factory):
    import xarray as xr
    outfile = tmp_path_factory.mktemp('data') / 'data.nc'
    xr.to_netcdf(data_array, str(outfile))
    return outfile
