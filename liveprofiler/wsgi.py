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

@uwsgidecorators.timer(2)
def collect(sig):
    log.info('Crontick from uwsgi timer, sig: {}'.format(sig))
    cfg = app.get_config(CONFIG)
    collector._collect(cfg['global']['dbpath'], cfg['collector']['hosts'], cfg['collector']['secret_header'])
