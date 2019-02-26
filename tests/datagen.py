import xarray as xr
import numpy as np
import pandas as pd

LONLIM = (-10, 12)
DLON = 0.25
LATLIM = (-1, 9)
DLAT = 0.25
LONLIM_SUBSET = (-5, 6)
LATLIM_SUBSET = (0, 7)

TSTART = '2000-01-01'

GRID_COORDS = dict(
    lon=np.arange(*LONLIM, DLON),
    lat=np.arange(*LATLIM, DLAT)
)

NAME = 'myvar'


def create_data_array(tstart=TSTART, ntime=12, freq='MS'):
    coords = GRID_COORDS.copy()
    coords.update(
        time=pd.date_range(tstart, periods=ntime, freq=freq)
    )
    dims = ['time', 'lat', 'lon']
    datashape = tuple((len(coords[key]) for key in dims))
    data = np.random.random(datashape)
    da = xr.DataArray(data, dims=dims, coords=coords, name=NAME)
    da.attrs.update(units='AU', long_name='My physical quantity')
    return da
