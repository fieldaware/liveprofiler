from stacksampler import ProfilingMiddleware
import model
import requests
import logging
from flask import Blueprint, current_app, jsonify

log = logging.getLogger('collector')

collector = Blueprint('collector', __name__, url_prefix='/collector')

def fetch_samples(host):
    profiling_path = ProfilingMiddleware.PROFILING_PATH
    secret_header = current_app.config['collector']['secret_header']
    url = 'http://{}/{}'.format(host, profiling_path)
    headers = {ProfilingMiddleware.SECRET_HEADER_NAME: secret_header}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    payload = resp.json()
    return payload['stacks']

@collector.route('/')
def collect():
    '''
    gets called periodically by uwsgi cron
    '''
    db = model.ProflingModel(current_app.config['global']['dbpath'])

    collected = 0
    for host in current_app.config['collector']['hosts']:
        try:
            stacks = fetch_samples(host)
            db.save(host, stacks)
            collected += len(stacks)
            log.info('Data collected host: {} stacks: {}'.format(host, len(stacks)))
        except Exception as exc:
            log.warning('Problem with collecting samples host: {}, exc: {}'.format(host, exc))
    return jsonify({'stacks_collected': collected})
