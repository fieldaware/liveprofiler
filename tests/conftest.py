import tempfile
import webtest
import pytest
import flask
from liveprofiler import stacksampler, model, app

SAMPLER_INTERVAL = 1
PROFILING_SECRET = 'secret'

application = flask.Flask(__name__)

samples = {
    u'elapsed': 1.2000219821929932,
    u'granularity': 0.001,
    u'stacks': [
        {u'count': 128, u'frame': u'test_sampler(test_sampler);testing_function2(test_sampler)'},
        {u'count': 126, u'frame': u'test_sampler(test_sampler);testing_function3(test_sampler)'},
        {u'count': 50, u'frame': u'test_sampler(test_sampler);testing_function(test_sampler)'},
        {u'count': 100, u'frame': u'test_sampler(test_sampler);testing_function(test_sampler)'}
    ]
}

@application.route('/')
def index():
    return 'app_endpoint'

@application.route('/post_test', methods=['POST'])
def post_test():
    return 'app_endpoint'

@pytest.fixture()
def simple_app(request):
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
def liveprofiler_app(request):
    db_dir = tempfile.mkdtemp()
    cfg_list = [
        '[global]',
        'DBPATH = {}'.format(db_dir),
        '[collector]',
        'secret_header = super!S3cr3t!',
        'hosts=localhost,otherhost.fa,google.com',
    ]

    _, cfg_path = tempfile.mkstemp()
    with open(cfg_path, 'w') as f:
        f.writelines('\n'.join(cfg_list))

    return webtest.TestApp(app.make_app(cfg_path))
