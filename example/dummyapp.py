from random import random
import time
from liveprofiler import stacksampler
import flask
import werkzeug.serving

app = flask.Flask(__name__)

@app.route('/sleep/')
def sleepy():
    time.sleep(random())
    return 'ok'

if __name__ == "__main__":
    with_stacksampler = stacksampler.ProfilingMiddleware(app, 0.001, 'super!S3cr3t!')
    werkzeug.serving.run_simple('localhost', 5000, with_stacksampler)
