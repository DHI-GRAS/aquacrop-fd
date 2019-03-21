TIME_ENCODING = dict(
    units="seconds since 1970-01-01 00:00:00",
    calendar="standard",
    dtype='float64')  # float64 for compatibility with NETCDF3_CLASSIC. int64 might be pereferable

NETCDF_FORMAT = 'NETCDF3_CLASSIC'

LATLON_ATTRIBUTES = {
    'lat': {
        'standard_name': 'latitude',
        'long_name': 'latitude',
        'units': 'degrees_north'},
    'lon': {
        'standard_name': 'longitude',
        'long_name': 'longitude',
        'units': 'degrees_east'}}

LATLON_ENCODING = {
    'lat': dict(dtype='float64'),
    'lon': dict(dtype='float64')}

CF_CONVENTIONS = 'CF-1.6'


def generate_xr_encoding_dict(ds):
    """Generate dictionary to feed to ds.to_netcdf(encoding={})"""
    encoding = {}
    if 'time' in ds.coords:
        encoding['time'] = TIME_ENCODING
    if 'lon' in ds.coords and 'lat' in ds.coords:
        encoding.update(LATLON_ENCODING)
    return encoding


def to_netcdf(ds, fname):
    """Save xarray.Dataset to file fname

    Parameters
    ----------
    ds : xarray.Dataset or xarray.DataArray
        input dataset
        DataArray will be converted
    fname : str
        path to output file (.nc)
    """
    for name in LATLON_ATTRIBUTES:
        ds[name].attrs.update(LATLON_ATTRIBUTES[name])

    # set output format
    kw = {'format': NETCDF_FORMAT}

    # figure out encoding
    encoding = generate_xr_encoding_dict(ds)
    if 'encoding' in kw:
        encoding.update(kw['encoding'])
    kw['encoding'] = encoding

    # set Conventions
    ds.attrs['Conventions'] = CF_CONVENTIONS
    return ds.to_netcdf(str(fname), **kw)
