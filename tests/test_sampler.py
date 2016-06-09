import conftest
from liveprofiler.stacksampler import ProfilingMiddleware

def test_middleware_happy_path(app):
    '''
    required: method GET, good PROFILER_TOKEN, request_path doesnt matter
    '''
    headers = {ProfilingMiddleware.SECRET_HEADER_NAME: conftest.PROFILING_SECRET}
    response = app.get('/liveprofiler', headers=headers).text
    assert 'elapsed ' in response
    assert 'granularity 1' in response

def test_middleware_wrong_secret(app):
    '''
    required: method GET, good PROFILER_TOKEN, request_path doesnt matter
    '''
    headers = {ProfilingMiddleware.SECRET_HEADER_NAME: 'wrong_secret'}
    response = app.get('/liveprofiler', headers=headers, status=403)
    assert response.status_code == 403

def test_middleware_wrong_secret_header_key(app):
    '''
    required: method GET, good PROFILER_TOKEN, request_path doesnt matter
    '''
    headers = {'wrong': conftest.PROFILING_SECRET}
    response = app.get('/liveprofiler', headers=headers, status=403)
    assert response.status_code == 403

def test_middleware_non_profiling_call(app):
    assert app.get('/').text == 'app_endpoint'
    assert app.post('/post_test').text == 'app_endpoint'
