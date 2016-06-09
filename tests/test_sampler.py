def test_foo(app):
    assert app.get('/', headers={'PROFILER_TOKEN': "SUPERSECRET"}).text == 'czesc'
