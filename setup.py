from setuptools import setup, find_packages

setup(
    name='aquacrop_fd',
    version='0.2.1',
    description='AquaCrop wrapper',
    url='https://github.com/DHI-GRAS/aquacrop-fd',
    author='Jonas Solvsteen',
    author_email='josl@dhigroup.com',
    entry_points="""
    [console_scripts]
    aquacrop-run=aquacrop_fd.scripts.cli:run_cli
    aquacrop-queues=aquacrop_fd.scripts.cli:run_queues
    """,
    install_requires=[
        'numpy',
        'xarray',
        'rasterio',
        'pandas',
        'affine',
        'click',
        'scipy',
        'dask',
        'netcdf4',
        'python-dateutil',
        'marshmallow==3.0.0rc1',
        'requests'
    ],
    extras_require={
        'test': [
            'pytest'
        ]
    },
    packages=find_packages(),
    include_package_data=True
)
