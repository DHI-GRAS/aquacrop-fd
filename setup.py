from setuptools import setup, find_packages

setup(
    name='aquacrop',
    version='0.1.0',
    description='AquaCrop wrapper',
    url='https://github.com/DHI-GRAS/aquacrop-fd',
    author='Jonas Solvsteen',
    author_email='josl@dhigroup.com',
    install_requires=[
        'xarray'
    ],
    extras_require={
        'test': [
            'pytest'
        ]
    },
    packages=find_packages(),
    include_package_data=True
)
