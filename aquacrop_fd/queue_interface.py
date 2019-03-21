import requests


def get_job(api_url):
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


def work_queue(api_url):

    while True:
        job = get_job(api_url)
        if job is None:
            break
