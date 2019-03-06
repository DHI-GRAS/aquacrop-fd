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
def data_dict_10d(data_array_10d):
    da = data_array_10d
    return dict(
        arrs=[da.isel(lon=5, lat=5).values],
        times=da.time.to_index().to_pydatetime()
    )


@pytest.fixture
def sample_config():
    return {
        'planting_date': datagen.TSTART,
        'crop': 'Maize',
        'soil': 'YoloClayLoam6'
    }


@pytest.fixture
def climate_file(tmp_path_factory, data_dict_10d):
    from aquacrop_fd import model_setup
    dst = tmp_path_factory.mktemp('climate') / 'Climate.TMP'
    model_setup.write_data_file(
        filename=dst.name,
        outdir=dst.parent,
        **data_dict_10d
    )
    return dst
