from stacksampler import ProfilingMiddleware
import model
import time
import requests
import logging

log = logging.getLogger('collector')

def collect(db, host, secret_header):
    profiling_path = ProfilingMiddleware.PROFILING_PATH
    url = 'http://{}/{}'.format(host, profiling_path)
    headers = {ProfilingMiddleware.SECRET_HEADER_NAME: secret_header}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError) as exc:
        log.warning('Error collecting data', error=exc, host=host)
        return
    payload = resp.json()
    try:
        db.save(host, payload)
    except Exception as exc:
        log.warning('Error saving data', error=exc, host=host)
        return
    log.info('Data collected', host=host, num_stacks=len(payload['stacks']))


def run(dbpath, host, secret_header, interval):
    db = model.ProflingModel(dbpath)
    while True:
        for h in host:
            collect(db, h, secret_header)
        time.sleep(interval)

if __name__ == '__main__':
    run()
