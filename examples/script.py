import datetime
import logging

from aquacrop_fd import interface

logging.basicConfig(level='INFO')

if __name__ == "__main__":

    geometry = {
            "type": "Polygon",
            "coordinates": [
              [
                [
                  95.38055419921875,
                  22.355156218589755
                ],
                [
                  95.73074340820312,
                  22.355156218589755
                ],
                [
                  95.73074340820312,
                  22.659640758754797
                ],
                [
                  95.38055419921875,
                  22.659640758754797
                ],
                [
                  95.38055419921875,
                  22.355156218589755
                ]
              ]
            ]
          }

    dsout = interface.interface(
        soil_map_path=r'C:\data\aquacrop\myanmar\soil-map-250m-reclassified-myanmar.tif',
        land_cover_path=r'C:\data\aquacrop\myanmar\land-cover-map-250m-myanmar.tif',
        plu_path=r'\\ncr641\E\FloodDroughtPortal\Myanmar_old\GPM\GPM_????.nc',
        tmp_max_path=r'C:\data\aquacrop\myanmar\monthly\tmn_min_monthly.nc',
        tmp_min_path=r'C:\data\aquacrop\myanmar\monthly\tmn_max_monthly.nc',
        eto_path=r'C:\data\aquacrop\myanmar\monthly\pet_mean_monthly.nc',
        geometry=geometry,
        crop='Maize',
        soil='SandyLoam',
        irrigated=True,
        planting_date=datetime.datetime(2018, 5, 1),
        nproc=None
    )

    print(dsout)
