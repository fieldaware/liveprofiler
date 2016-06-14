import responses
from conftest import samples


@responses.activate
def test_visualizer_collector(visualizer_app):
    hosts = visualizer_app.app.config['collector']['hosts']

    for host in hosts:
        responses.add(
            responses.GET, 'http://{}/liveprofiler'.format(host),
            json=samples, status=200
        )

    res = visualizer_app.get('/collector/')
