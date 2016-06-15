import pytest
import mock
import responses
from conftest import samples
from liveprofiler.model import ProflingModel

@pytest.mark.liveprofiler_app(hosts='localhost,otherhost.fa,google.com')
@responses.activate
def test_collector_happy_path(liveprofiler_app):
    hosts = liveprofiler_app.app.config['collector']['hosts']

    for host in hosts:
        responses.add(
            responses.GET, 'http://{}/liveprofiler'.format(host),
            json=samples, status=200
        )

    with mock.patch('time.time', return_value=1):
        res = liveprofiler_app.get('/collector/')

    assert res.json == {'stacks_collected': 3 * 4}  # 4 stacks * 3 hosts
    saved_localhost = ProflingModel(liveprofiler_app.app.config['global']['dbpath']).load('localhost')
    saved_otherhost = ProflingModel(liveprofiler_app.app.config['global']['dbpath']).load('otherhost.fa')
    saved_googleco = ProflingModel(liveprofiler_app.app.config['global']['dbpath']).load('google.com')

    for loaded in (saved_googleco, saved_localhost, saved_otherhost):
        assert len(loaded) == 3
        assert (['test_sampler(test_sampler)', 'testing_function3(test_sampler)'], 126) in loaded
        assert (['test_sampler(test_sampler)', 'testing_function2(test_sampler)'], 128) in loaded
        assert (['test_sampler(test_sampler)', 'testing_function(test_sampler)'], 150) in loaded


@pytest.mark.liveprofiler_app(hosts='localhost')
@pytest.mark.parametrize('error_code', (400, 401, 403, 404, 500, 502, 503))
@responses.activate
def test_collector_host_collect_errors(liveprofiler_app, error_code):
    responses.add(responses.GET, 'http://localhost/liveprofiler', status=error_code)
    res = liveprofiler_app.get('/collector/')
    assert res.json == {'stacks_collected': 0}
