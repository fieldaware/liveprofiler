import webtest
import pytest
import flask
from liveprofiler import stacksampler

SAMPLER_INTERVAL = 1
PROFILING_SECRET = 'secret'

application = flask.Flask(__name__)

@application.route('/')
def index():
    return 'app_endpoint'

@application.route('/post_test', methods=['POST'])
def post_test():
    return 'app_endpoint'

@pytest.fixture()
def app(request):
    with_middleware = stacksampler.ProfilingMiddleware(application, SAMPLER_INTERVAL, PROFILING_SECRET)
    return webtest.TestApp(with_middleware)
