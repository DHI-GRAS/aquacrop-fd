from setuptools import setup, find_packages

setup(
    name='aquacrop_fd',
    version='0.1.0',
    description='AquaCrop wrapper',
    url='https://github.com/DHI-GRAS/aquacrop-fd',
    author='Jonas Solvsteen',
    author_email='josl@dhigroup.com',
    entry_points="""
    [console_scripts]
    aquacrop-run=aquacrop_fd.scripts:run_cli
    """,
    install_requires=[
        'numpy',
        'xarray',
        'rasterio',
        'pandas',
        'affine',
        'click',
        'python-dateutil'
    ],
    extras_require={
        'test': [
            'pytest'
        ]
    },
    packages=find_packages(),
    include_package_data=True
)
