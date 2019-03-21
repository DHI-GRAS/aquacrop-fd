import requests

from aquacrop_fd import interface
from aquacrop_fd import queue_schemas


def get_job(api_url):
    return {
        'fraction': 80.0,
        'geometry': {'type': 'Rectangle',
                     'coordinates': [[[-3.6035156249999996, 10.708109848387668],
                                      [-3.6035156249999996, 11.82864282964517],
                                      [-2.5048828125, 11.82864282964517],
                                      [-2.5048828125, 10.708109848387668]]]},
        'area_name': 'Volta',
        'guid': '9cc4dd76-7417-446a-8245-26412322c907',
        'planting_date': '2019-01-01',
        'crop': 'Maize',
        'irrigated': False
    }

    url = api_url + '/getjob'
    r = requests.post(url, json={'num_messages': 1})
    if not r.ok:
        if 'No message found' in r.text:
            return None
        else:
            raise RuntimeError(
                f'Request failed with message {r.text}'
            )
    return r.json()


def work_queue(
        api_url,
        plu_path, eto_path, tmp_min_path, tmp_max_path,
        soil_map_path, land_cover_path
):
    if not api_url.endswith('/'):
        api_url = api_url + '/'

    while True:
        job = get_job(api_url)
        if job is None:
            break

        schema = queue_schemas.JobSchema()
        jobkw = schema.load(job)

        interface(
            plu_path=plu_path, eto_path=eto_path,
            tmp_min_path=tmp_min_path, tmp_max_path=tmp_max_path,
            soil_map_path=soil_map_path, land_cover_path=land_cover_path,
            **jobkw
        )
