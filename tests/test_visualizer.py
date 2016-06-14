import responses
import os.path
from liveprofiler import visualizer
from conftest import samples

here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

def test_config_load_to_dict():
    config = visualizer.get_config(here('example_configuration.ini'))

    assert {
        'global': {'dbpath': '/tmp/test'},
        'collector': {
            'hosts': ['localhost', 'otherhost.fa', 'google.com'],
            'secret_header': 'super!S3cr3t!',
        }} == config

@responses.activate
def test_visualizer_collector(visualizer_app):
    hosts = visualizer_app.app.config['collector']['hosts']

    for host in hosts:
        responses.add(
            responses.GET, 'http://{}/liveprofiler'.format(host),
            json=samples, status=200
        )

    res = visualizer_app.get('/collector/')
