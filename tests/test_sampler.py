import json
import time
import conftest
from liveprofiler.stacksampler import ProfilingMiddleware

def test_middleware_happy_path(app):
    '''
    required: method GET, good PROFILER_TOKEN, request_path doesnt matter
    '''
    headers = {ProfilingMiddleware.SECRET_HEADER_NAME: conftest.PROFILING_SECRET}
    response = json.loads(app.get('/liveprofiler', headers=headers).text)
    assert 'elapsed' in response.keys()
    assert response['granularity'] == 1

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


def test_sampler(sampler):
    def testing_function():
        now = time.time()
        while time.time() < now + 0.2:
            pass

    def testing_function2():
        now = time.time()
        while time.time() < now + 0.4:
            pass

    def testing_function3():
        now = time.time()
        while time.time() < now + 0.6:
            pass

    sampler.start()

    testing_function3()
    testing_function()
    testing_function2()

    stats = json.loads(sampler.output_stats())

    sampler.stop()
    # at least time of execution of testing_function2 and testing_function
    assert stats >= 1.5

    # stacks are sorted by stack counts which is correlated with the function duration
    assert 'test_sampler(test_sampler);testing_function(test_sampler)' in stats['stacks'][2]['frame']
    assert 'test_sampler(test_sampler);testing_function2(test_sampler)' in stats['stacks'][1]['frame']
    assert 'test_sampler(test_sampler);testing_function3(test_sampler)' in stats['stacks'][0]['frame']

    # number of collected samples depends on the sampler inteval and duration of stack execution
    assert 0.2 / sampler.interval >= float(stats['stacks'][2]['count'])
    assert 0.4 / sampler.interval >= float(stats['stacks'][1]['count'])
    assert 0.6 / sampler.interval >= float(stats['stacks'][0]['count'])
