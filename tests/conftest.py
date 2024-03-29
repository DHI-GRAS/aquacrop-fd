import sys

import pytest

import datagen


def pytest_runtest_setup(item):
    m = item.get_closest_marker('skiplinux')
    if m is not None and sys.platform != 'win32':
        pytest.skip('For some reason not working on Linux.')


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
def data_dict_10d(data_array_10d):
    from aquacrop_fd import model_setup
    data = {
        name: [data_array_10d.isel(lon=5, lat=5).values.copy()]
        for name in model_setup.REQUIRED_CLIMATE_FILES
    }
    data['Climate.TMP'] = data['Climate.TMP'] * 2
    data['time'] = data_array_10d.time.to_index().to_pydatetime()
    return data


@pytest.fixture
def sample_config():
    return {
        'planting_date': datagen.TSTART,
        'crop': 'Maize',
        'soil': 'YoloClayLoam6',
        'irrigated': True
    }


@pytest.fixture
def climate_file(tmp_path_factory, data_dict_10d):
    from aquacrop_fd import model_setup
    dst = tmp_path_factory.mktemp('climate') / 'Climate.PLU'
    model_setup.write_climate_file(
        filename=dst.name,
        datadir=dst.parent,
        arrs=data_dict_10d['Climate.PLU'],
        time=data_dict_10d['time']
    )
    return dst


@pytest.fixture(scope='session')
def soil_map_file(tmp_path_factory):
    import rasterio
    import affine
    import numpy as np
    path = tmp_path_factory.mktemp('aux') / 'soil-map.tif'
    data = np.random.randint(0, 11 + 1, size=(1, 200, 300)).astype('uint8')
    data[data == 11] = 255
    data[0, 0] = 3
    profile = {
        'width': data.shape[-1],
        'height': data.shape[-2],
        'count': data.shape[0],
        'nodata': 255,
        'dtype': data.dtype,
        'driver': 'GTiff',
        'crs': {'init': 'epsg:4326'},
        'transform': affine.Affine(0.002, 0, 0, 0, -0.002, 0)
    }
    with rasterio.open(path, 'w', **profile) as dst:
        dst.write(data)
    return path
