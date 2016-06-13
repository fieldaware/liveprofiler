import os.path
from liveprofiler import visualizer

here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

def test_config_load_to_dict():
    config = visualizer.get_config(here('example_configuration.ini'))

    assert {
        'global': {'dbpath': '/tmp/test'},
        'collector': {
            'hosts': ['localhost', 'otherhost.fa', 'google.com'],
            'secret_header': 'super!S3cr3t!',
        }} == config

def test_visualizer_collector(visualizer_app):
    visualizer_app.get('/collector/')
