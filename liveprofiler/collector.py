from stacksampler import ProfilingMiddleware
import model
import requests
import logging
from flask import Blueprint, current_app, jsonify
from urlparse import urljoin

log = logging.getLogger('collector')

collector = Blueprint('collector', __name__, url_prefix='/collector')

def fetch_samples(host):
    profiling_path = ProfilingMiddleware.PROFILING_PATH
    secret_header = current_app.config['collector']['secret_header']
    url = urljoin('http://{}'.format(host), profiling_path)
    headers = {ProfilingMiddleware.SECRET_HEADER_NAME: secret_header}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    payload = resp.json()
    return payload

@collector.route('/')
def collect():
    '''
    gets called periodically by uwsgi cron
    '''
    db = model.ProflingModel(current_app.config['global']['dbpath'])

    collected = 0
    for host in current_app.config['collector']['hosts']:
        samples = fetch_samples(host)
        db.save(host, samples)
        stacks_count = len(samples['stacks'])
        collected += stacks_count
        log.info('Data collected host: {} stacks: {}'.format(host, stacks_count))
    return jsonify({'stacks_collected': collected})
