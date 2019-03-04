from pathlib import Path
import shutil

import pytest

import datagen


@pytest.fixture
def data_array_ms():
    return datagen.create_data_array(freq='MS', ntime=12)


@pytest.fixture
def data_array_10d():
    return datagen.create_data_array(freq='10D', ntime=30)


@pytest.fixture
def data_file_ms(data_array_ms, tmp_path_factory):
    import xarray as xr
    outfile = tmp_path_factory.mktemp('data_ms') / 'data.nc'
    xr.to_netcdf(data_array_ms, str(outfile))
    return outfile


@pytest.fixture
def data_file_10d(data_array_10d, tmp_path_factory):
    import xarray as xr
    outfile = tmp_path_factory.mktemp('data_10d') / 'data.nc'
    xr.to_netcdf(data_array_10d, str(outfile))
    return outfile


@pytest.fixture
def climate_file(tmp_path_factory):
    from aquacrop_fd import templates
    climfile = Path(templates.__file__).parent / 'climate' / 'Climate.TMP'
    dst = tmp_path_factory.mktemp('climate') / climfile.name
    shutil.copy(climfile, dst)
    return dst
