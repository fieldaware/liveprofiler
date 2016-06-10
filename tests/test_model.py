import mock
import os
import dbm
from datetime import datetime

def test_db_ctx_manager(db):
    with db.getdb() as d:
        d['foo'] = 'bar'

    with db.getdb() as d:
        assert d['foo'] == 'bar'


def test_db_path(db):
    now = datetime.now()
    expected_db_name = "{}_{}_{}".format(now.year, now.month, now.day)
    with db.getdb() as d:
        d['key'] = 'value'
    assert dbm.open(os.path.join(db.dbdir, expected_db_name))['key'] == 'value'


def test_save(db):
    samples = {
        u'elapsed': 1.2000219821929932,
        u'granularity': 0.001,
        u'stacks': [
            {u'count': 128, u'frame': u'test_sampler(test_sampler);testing_function2(test_sampler)'},
            {u'count': 126, u'frame': u'test_sampler(test_sampler);testing_function3(test_sampler)'},
            {u'count': 50, u'frame': u'test_sampler(test_sampler);testing_function(test_sampler)'}
        ]
    }
    with mock.patch('time.time', return_value=1):
        db.save('localhost', samples)

    with db.getdb() as d:
        assert dict([(k, d[k]) for k in d.keys()]) == {
            'test_sampler(test_sampler);testing_function(test_sampler)': '{"count": 50, "host": "localhost", "time": 1}',
            'test_sampler(test_sampler);testing_function2(test_sampler)': '{"count": 128, "host": "localhost", "time": 1}',
            'test_sampler(test_sampler);testing_function3(test_sampler)': '{"count": 126, "host": "localhost", "time": 1}'
        }
