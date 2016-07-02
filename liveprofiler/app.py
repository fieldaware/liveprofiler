from ConfigParser import RawConfigParser
from flask import Flask
import click
from distutils.util import strtobool

from collector import collector
from visualizer import visualizer
import liveprofiler_sampler

def wrap_with_profiling_middleware(app, config):
    if not config or not strtobool(config.get('enabled')):
        return app
    interval = config.get('interval')
    secret_header = config.get('secret_header')
    return liveprofiler_sampler.ProfilingMiddleware(app, interval, secret_header)

def make_app(cfg_path):
    app = Flask('liveprofiler')

    cfg = get_config(cfg_path)
    app.config.update(**cfg)

    app.register_blueprint(collector)
    app.register_blueprint(visualizer)

    app.wsgi_app = wrap_with_profiling_middleware(app.wsgi_app, cfg.get('sampler'))

    return app

def get_config(path):
    cfgobj = RawConfigParser()
    cfgobj.read(path)
    cfg = dict([(section, dict(cfgobj.items(section))) for section in cfgobj.sections()])
    assert cfg.get('global', {}).get('dbpath'), 'dbpath is required'
    assert cfg.get('collector', {}).get('secret_header'), 'secret_header is required'
    assert cfg.get('collector', {}).get('hosts'), 'hosts required'

    cfg['collector']['hosts'] = cfg['collector']['hosts'].split(',')
    return cfg

@click.command()
@click.option('--cfg_path', type=str)
@click.option('--port', type=int, default=9999)
@click.option('--debug', default=True)
def run(cfg_path, port, debug):
    app = make_app(cfg_path)
    import logging.config
    logging.config.fileConfig(cfg_path)
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    run()
