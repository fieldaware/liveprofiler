import uwsgi
CONFIG = uwsgi.opt.get('app_config')  # uwsgi --set app_config=/path/config.ini
assert CONFIG is not None, 'MISSING CONFIG PARAM'

import logging.config
logging.config.fileConfig(CONFIG)
log = logging.getLogger(__name__)

from liveprofiler import app
application = app.make_app(CONFIG)

from liveprofiler import collector
import uwsgidecorators

def __start_collector():
    cfg = app.get_config(CONFIG)
    interval = int(cfg['collector'].get('interval', 60))
    dbpath = cfg['global']['dbpath']
    hosts = cfg['collector']['hosts']
    secret_header = cfg['collector']['secret_header']

    @uwsgidecorators.timer(interval)
    def ticker(sig):
        log.info('Crontick from uwsgi timer, sig: {}'.format(sig))
        collector._collect(dbpath, hosts, secret_header)

__start_collector()
