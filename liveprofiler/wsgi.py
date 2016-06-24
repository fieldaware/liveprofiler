import uwsgi
CONFIG = uwsgi.opt.get('app_config')  # uwsgi --set app_config=/path/config.ini
assert CONFIG is not None, 'MISSING CONFIG PARAM'

import logging.config
logging.config.fileConfig(CONFIG)

from liveprofiler import app
application = app.make_app(CONFIG)
