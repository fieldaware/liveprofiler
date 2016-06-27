import tempfile
import webtest
import pytest
from liveprofiler import model, app

SAMPLER_INTERVAL = 1
PROFILING_SECRET = 'secret'

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

@pytest.fixture()
def db(request):
    d = tempfile.mkdtemp()
    return model.ProflingModel(d)

@pytest.fixture()
def liveprofiler_app(request):
    fix_params = request.node.get_marker('liveprofiler_app').kwargs
    db_dir = tempfile.mkdtemp()
    cfg_list = [
        '[global]',
        'DBPATH = {}'.format(db_dir),
        '[collector]',
        'secret_header = super!S3cr3t!',
        'hosts={}'.format(fix_params['hosts']),
    ]

    _, cfg_path = tempfile.mkstemp()
    with open(cfg_path, 'w') as f:
        f.writelines('\n'.join(cfg_list))

    return webtest.TestApp(app.make_app(cfg_path))
