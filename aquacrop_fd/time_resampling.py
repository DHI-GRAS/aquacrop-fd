import xarray as xr


def times_at_year(da, year):
    return [d.replace(year=year) for d in da['time'].to_index().to_pydatetime()]


def da_at_year(da, year):
    da = da.copy()
    vals = times_at_year(da, year)
    time = da['time'].copy()
    time.values = vals
    da['time'] = time
    return da


def interpolate_monthly_means(da, time_index):
    """Interpolate monthly means to new time_index

    Parameters
    ----------
    da : DataArray
        data to interpolate
    time_index : pandas.DatetimeIndex
        where to interpolate at

    Returns
    -------
    DataArray
        interpolated data
    """
    years = sorted(time_index.year.unique())
    dada = []
    for year in years:
        da_year = da_at_year(da, year)
        dada.append(da_year)
    da_years = xr.concat(dada, dim='time')
    return da_years.interp(time=time_index, method='linear')


def index_doy_means(da, time_index):
    """Index a DataArray of day-of-year means to match time_index

    Parameters
    ----------
    da : DataArray
        data to index
    time_index : pandas.DatetimeIndex
        where to index at

    Returns
    -------
    DataArray
        indexed data
    """
    if not len(da.time) == 366:
        raise ValueError(
            f'Expecting dataset with 366 time steps. Got {da.time}.'
        )
    dasel = da.isel(time=time_index.dayofyear)
    dasel['time'].values = time_index
    return dasel


def resample_means(da, time_index):
    """Resample inter-annual mean at time_index

    Parameters
    ----------
    da : DataArray
        data to resample
    time_index : pandas.DatetimeIndex
        what to resample to

    Returns
    -------
    DataArray
        resampled data
    """

    if len(da.time) == 366:
        return index_doy_means(da, time_index)
    else:
        return interpolate_monthly_means(da, time_index)
