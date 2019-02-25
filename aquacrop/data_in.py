from pathlib import Path

import xarray as xr

from aquacrop import templates


def write_temperature(ds, outdir):

    ds.resample()
