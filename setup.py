from setuptools import setup, find_packages

setup(
    name='aquacrop',
    description='AquaCrop wrapper',
    url='https://github.com/DHI-GRAS/aquacrop-fd',
    author='Jonas Solvsteen',
    author_email='josl@dhigroup.com',
    install_requires=[
        'xarray',
        'rasterio'
    ],
    packages=find_packages()
)
