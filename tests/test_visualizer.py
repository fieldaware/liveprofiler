import pytest

@pytest.mark.liveprofiler_app(hosts='localhost')
def test_index_render(liveprofiler_app):
    assert liveprofiler_app.get('/').text != ''
