import model
import requests
import logging
from flask import Blueprint, current_app, jsonify
from urlparse import urljoin

log = logging.getLogger('collector')

collector = Blueprint('collector', __name__, url_prefix='/collector')

PROFILING_PATH = '/liveprofiler'
SECRET_HEADER_NAME = 'PROFILER_TOKEN'

def fetch_samples(host, secret_header):
    log.info('Fetching {}'.format(host))
    profiling_path = PROFILING_PATH
    url = urljoin('http://{}'.format(host), profiling_path)
    headers = {SECRET_HEADER_NAME: secret_header}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        log.warning('Calling {} resulted in error: {}'.format(host, e.message))
        return
    try:
        payload = resp.json()
    except ValueError as e:
        log.warning('Response from {} is not a valid json: {}'.format(host, resp.text))
        return
    return payload


def _collect(dbpath, hosts, secret_header):
    db = model.ProflingModel(dbpath)
    collected = 0
    for host in hosts:
        samples = fetch_samples(host, secret_header)
        if not samples:
            log.warning('No samples has been collected from: {}'.format(host))
            continue
        db.save(host, samples)
        stacks_count = len(samples['stacks'])
        collected += stacks_count
        log.info('Data collected host: {} stacks: {}'.format(host, stacks_count))
    return {'stacks_collected': collected}

@collector.route('/')
def collect():
    '''
    gets called periodically by uwsgi cron
    '''
    dbpath = current_app.config['global']['dbpath']
    hosts = current_app.config['collector']['hosts']
    secret = current_app.config['collector']['secret_header']
    return jsonify(_collect(dbpath, hosts, secret))
