from pathlib import Path

import xarray as xr

from aquacrop_fd import templates


def write_temperature(ds, outdir):

    ds.resample()
