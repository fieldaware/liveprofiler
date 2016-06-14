import json
import mock
import os
import dbm
from datetime import datetime
from conftest import samples

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
    with mock.patch('time.time', return_value=1):
        db.save('localhost', samples)

    with db.getdb() as d:
        records = dict([(k, d[k]) for k in d.keys()])

        assert {"count": 50, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function(test_sampler)'])
        assert {"count": 100, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function(test_sampler)'])
        assert {"count": 128, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function2(test_sampler)'])
        assert {"count": 126, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function3(test_sampler)'])

    with mock.patch('time.time', return_value=2):
        db.save('localhost', samples)

    with db.getdb() as d:
        records = dict([(k, d[k]) for k in d.keys()])
        assert {"count": 50, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function(test_sampler)'])
        assert {"count": 100, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function(test_sampler)'])
        assert {"count": 128, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function2(test_sampler)'])
        assert {"count": 126, "host": "localhost", "time": 1} in json.loads(records['test_sampler(test_sampler);testing_function3(test_sampler)'])

        assert {"count": 50, "host": "localhost", "time": 2} in json.loads(records['test_sampler(test_sampler);testing_function(test_sampler)'])
        assert {"count": 100, "host": "localhost", "time": 2} in json.loads(records['test_sampler(test_sampler);testing_function(test_sampler)'])
        assert {"count": 128, "host": "localhost", "time": 2} in json.loads(records['test_sampler(test_sampler);testing_function2(test_sampler)'])
        assert {"count": 126, "host": "localhost", "time": 2} in json.loads(records['test_sampler(test_sampler);testing_function3(test_sampler)'])

def test_load(db):
    with mock.patch('time.time', return_value=1):
        db.save('localhost', samples)

    loaded = db.load(host='localhost')
    assert (['test_sampler(test_sampler)', 'testing_function3(test_sampler)'], 126) in loaded
    assert (['test_sampler(test_sampler)', 'testing_function2(test_sampler)'], 128) in loaded
    # sum of 100 and 50
    assert (['test_sampler(test_sampler)', 'testing_function(test_sampler)'], 150) in loaded

    assert db.load('otherhost') == []
