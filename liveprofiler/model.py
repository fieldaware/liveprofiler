import json
from datetime import datetime
import time
import contextlib
import dbm
from os.path import join

class ProflingModel(object):
    def __init__(self, dbdir):
        assert dbdir.startswith('/')
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
        with self.getdb() as db:
            for stack in samples['stacks']:
                frame = stack['frame']
                entry = json.dumps(dict(host=host, time=now, count=stack['count']))
                if frame in db:
                    db[frame] += entry
                else:
                    db[frame] = entry
