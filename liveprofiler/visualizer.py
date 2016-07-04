import calendar
import dateparser

from flask import request, jsonify, Blueprint, current_app, render_template
import logging
import logging.config

import model

log = logging.getLogger('visualizer')

visualizer = Blueprint('visualizer', __name__, url_prefix='/', template_folder='templates', static_folder='static')

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


@visualizer.route('graph/<host>/')
def graph(host):
    return render_template('graph.html', host=host)

@visualizer.route('/')
def index():
    return render_template('index.html', hosts=current_app.config['collector']['hosts'])

@visualizer.route('profile/<host>/')
def profile(host):
    from_ = request.args.get('from')
    if from_ is not None:
        from_ = _parse_relative_date(from_)
    until = request.args.get('until')
    if until is not None:
        until = _parse_relative_date(until)
    threshold = float(request.args.get('threshold', 0))
    root = Node('root')
    db = model.ProflingModel(current_app.config['global']['dbpath'])
    for frames, value in db.load(host):
        root.add(frames, value)
    return jsonify(root.serialize(threshold * root.value))
