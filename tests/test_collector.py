import mock
import responses
from conftest import samples
from liveprofiler.model import ProflingModel

@responses.activate
def test_collector(liveprofiler_app):
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

    assert [(['test_sampler(test_sampler)', 'testing_function3(test_sampler)'], 126),
            (['test_sampler(test_sampler)', 'testing_function2(test_sampler)'], 128),
            (['test_sampler(test_sampler)', 'testing_function(test_sampler)'], 150)] \
        == saved_googleco == saved_localhost == saved_otherhost
