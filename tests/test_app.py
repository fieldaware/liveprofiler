import os.path
from liveprofiler import app
here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

def test_config_load_to_dict():
    config = app.get_config(here('example_configuration.ini'))

    assert {
        'global': {'dbpath': '/tmp/test'},
        'collector': {
            'hosts': ['localhost', 'otherhost.fa', 'google.com'],
            'secret_header': 'super!S3cr3t!',
        }} == config
