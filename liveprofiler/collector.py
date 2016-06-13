import model
import time
import click
import requests
import logging

log = logging.getLogger('collector')

def collect(dbpath, host, port, db):
    try:
        resp = requests.get('http://{}:{}?reset=true'.format(host, port))
        resp.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError) as exc:
        log.warning('Error collecting data', error=exc, host=host, port=port)
        return
    payload = resp.json()
    try:
        db.save(payload, host, port, dbpath)
    except Exception as exc:
        log.warning('Error saving data', error=exc, host=host, port=port)
        return
    log.info('Data collected', host=host, port=port, num_stacks=len(payload['stack']))


@click.command()
@click.option('--dbpath', '-d', default='/var/lib/stackcollector/db')
@click.option('--host', '-h', multiple=True)
@click.option('--interval', '-i', type=int, default=600)
@click.option('--secret_header', '-s', type=str)
def run(dbpath, host, secret_header, interval):
    # TODO(emfree) document port format; handle parsing errors
    db = model.ProflingModel(dbpath)
    while True:
        for h in host:
            collect(dbpath, h, secret_header, db)
        time.sleep(interval)

if __name__ == '__main__':
    run()
