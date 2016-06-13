import calendar
import click
import dateparser
import requests

from ConfigParser import SafeConfigParser
from flask import Flask, request, jsonify, Blueprint, current_app
import logging
import logging.config

import model
from stacksampler import ProfilingMiddleware

log = logging.getLogger('visualizer')

def get_config(path):
    cfgobj = SafeConfigParser()
    cfgobj.read(path)
    cfg = dict([(section, dict(cfgobj.items(section))) for section in cfgobj.sections()])
    assert cfg.get('global', {}).get('dbpath'), 'DBPATH is required'
    assert cfg.get('collector', {}).get('secret_header'), 'secret_header is required'
    assert cfg.get('collector', {}).get('hosts'), 'hosts required'

    cfg['collector']['hosts'] = cfg['collector']['hosts'].split(',')
    return cfg

dashboard = Blueprint('dashboard', __name__, url_prefix='/', static_folder='static')
collector = Blueprint('collector', __name__, url_prefix='/collector')

def _parse_relative_date(datestr):
    return calendar.timegm(dateparser.parse(datestr).utctimetuple())

class Node(object):
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.children = {}

    def serialize(self, threshold=None):
        res = {
            'name': self.name,
            'value': self.value
        }
        if self.children:
            serialized_children = [
                child.serialize(threshold)
                for _, child in sorted(self.children.items())
                if child.value > threshold
            ]
            if serialized_children:
                res['children'] = serialized_children
        return res

    def add(self, frames, value):
        self.value += value
        if not frames:
            return
        head = frames[0]
        child = self.children.get(head)
        if child is None:
            child = Node(name=head)
            self.children[head] = child
        child.add(frames[1:], value)

    def add_raw(self, line):
        frames, value = line.split()
        frames = frames.split(';')
        try:
            value = int(value)
        except ValueError:
            return
        self.add(frames, value)

@collector.route('/')
def collect():
    '''
    gets called periodically by uwsgi cron
    '''
    db = model.ProflingModel(current_app.config['global']['dbpath'])
    profiling_path = ProfilingMiddleware.PROFILING_PATH
    secret_header = current_app.config['collector']['secret_header']

    collected = 0
    for host in current_app.config['collector']['hosts']:
        try:
            url = 'http://{}/{}'.format(host, profiling_path)
            headers = {ProfilingMiddleware.SECRET_HEADER_NAME: secret_header}
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            payload = resp.json()
            db.save(host, payload)
            collected += len(payload['stacks'])
            log.info('Data collected host: {} stacks: {}'.format(host, len(payload['stacks'])))
        except Exception as exc:
            log.warning('Problem with collecting samples host: {}, exc: {}'.format(host, exc))
    return jsonify({'stacks_collected': collected})

@dashboard.route('/data')
def data():
    from_ = request.args.get('from')
    if from_ is not None:
        from_ = _parse_relative_date(from_)
    until = request.args.get('until')
    if until is not None:
        until = _parse_relative_date(until)
    threshold = float(request.args.get('threshold', 0))
    root = Node('root')
    db = model.ProflingModel(current_app.config['global']['DBPATH'])
    for frames, value in db.load():
        root.add(frames, value)
    return jsonify(root.serialize(threshold * root.value))

@dashboard.route('/')
def render():
    return dashboard.send_static_file('index.html')

def make_app(cfg_path):
    app = Flask('liveprofiler')
    cfg = get_config(cfg_path)
    app.config.update(**cfg)
    app.register_blueprint(collector)
    app.register_blueprint(dashboard)
    return app

@click.command()
@click.option('--cfg_path', type=str)
@click.option('--port', type=int, default=9999)
@click.option('--debug', default=True)
def run(cfg_path, port, debug):
    app = make_app(cfg_path)
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    run()
