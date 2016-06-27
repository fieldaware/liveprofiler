from collections import defaultdict
import json
from datetime import datetime
import time
import contextlib
import dbm
from os.path import join
import os

STACK_SEPARATOR = ';'

class ProflingModel(object):
    def __init__(self, dbdir):
        assert dbdir.startswith('/')
        if not os.path.isdir(dbdir):
            os.makedirs(dbdir)
        self.dbdir = dbdir

    @contextlib.contextmanager
    def getdb(self):
        while True:
            try:
                handle = dbm.open(self.db_path(), 'c')
                break
            except dbm.error as exc:
                if exc.args[0] == 11:
                    continue
                else:
                    raise
        try:
            yield handle
        finally:
            handle.close()

    def db_path(self):
        now = datetime.now()
        return join(self.dbdir, '{}_{}_{}'.format(now.year, now.month, now.day))

    def save(self, host, samples):
        now = int(time.time())
        entries = defaultdict(list)
        for stack in samples['stacks']:
            entries[stack['frame']].append(dict(host=host, time=now, count=stack['count']))

        with self.getdb() as db:
            for frame, entires in entries.items():
                if frame in db:
                    current_entires = json.loads(db[frame])
                    current_entires.extend(entires)
                    db[frame] = json.dumps(current_entires)
                else:
                    db[frame] = json.dumps(entires)

    def load(self, host, from_=None, until_=None):
        ''' might return results in random order '''
        results = []
        with self.getdb() as db:
            keys = db.keys()
            for k in keys:
                entries = json.loads(db[k])
                value = 0
                for e in entries:
                    if e['host'] != host:
                        continue
                    ts = int(e['time'])
                    v = int(e['count'])
                    if (from_ is None or ts >= from_) and (until_ is None or ts <= until_):
                        value += v
                frames = k.split(STACK_SEPARATOR)
                if value:
                    results.append((frames, value))
        return results
