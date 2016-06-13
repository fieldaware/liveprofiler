import calendar
import click
import dateparser
from flask import Flask, request, jsonify, Blueprint, current_app
import model

dashboard = Blueprint('dashboard', __name__, url_prefix='/', static_folder='static')

def _parse_relative_date(datestr):
    return calendar.timegm(dateparser.parse(datestr).utctimetuple())


class Node(object):
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.children = {}

    def serialize(self, threshold=None):
        res = {
            'name': self.name,
            'value': self.value
        }
        if self.children:
            serialized_children = [
                child.serialize(threshold)
                for _, child in sorted(self.children.items())
                if child.value > threshold
            ]
            if serialized_children:
                res['children'] = serialized_children
        return res

    def add(self, frames, value):
        self.value += value
        if not frames:
            return
        head = frames[0]
        child = self.children.get(head)
        if child is None:
            child = Node(name=head)
            self.children[head] = child
        child.add(frames[1:], value)

    def add_raw(self, line):
        frames, value = line.split()
        frames = frames.split(';')
        try:
            value = int(value)
        except ValueError:
            return
        self.add(frames, value)


@dashboard.route('/data')
def data():
    from_ = request.args.get('from')
    if from_ is not None:
        from_ = _parse_relative_date(from_)
    until = request.args.get('until')
    if until is not None:
        until = _parse_relative_date(until)
    threshold = float(request.args.get('threshold', 0))
    root = Node('root')
    db = model.ProflingModel(current_app.config['DBPATH'])
    for frames, value in db.load():
        root.add(frames, value)
    return jsonify(root.serialize(threshold * root.value))


@dashboard.route('/')
def render():
    return dashboard.send_static_file('index.html')


def make_app(cfg):
    app = Flask('liveprofiler')
    app.config.update(**cfg)
    return app

@click.command()
@click.option('--port', type=int, default=9999)
@click.option('--dbpath', '-d', default='/var/lib/stackcollector/db')
@click.option('--debug', default=False)
def run(port, dbpath, debug):
    config = {'DBPATH': dbpath}
    app = make_app(config)
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    run()
