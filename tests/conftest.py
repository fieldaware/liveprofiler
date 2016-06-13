import tempfile
import webtest
import pytest
import flask
from liveprofiler import stacksampler, model, visualizer

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

@pytest.fixture()
def db(request):
    d = tempfile.mkdtemp()
    return model.ProflingModel(d)

@pytest.fixture()
def sampler(request):
    return stacksampler.Sampler(0.001)

@pytest.fixture()
def visualizer_app(request):
    cfg_list = [
        '[global]',
        'DBPATH = /tmp/test',
        '[collector]',
        'secret_header = super!S3cr3t!',
        'hosts=localhost,otherhost.fa,google.com',
    ]

    _, cfg_path = tempfile.mkstemp()
    with open(cfg_path, 'w') as f:
        f.writelines('\n'.join(cfg_list))

    return webtest.TestApp(visualizer.make_app(cfg_path))
