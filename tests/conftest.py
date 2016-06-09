import webtest
import pytest
import flask
from liveprofiler import stacksampler

SAMPLER_INTERVAL = 1

application = flask.Flask(__name__)

@application.route('/')
def index():
    return 'czesc'


@pytest.fixture()
def app(request):
    return webtest.TestApp(stacksampler.ProfilingMiddleware(application, SAMPLER_INTERVAL))
