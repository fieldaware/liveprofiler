"""
Statistical profiling for long-running Python processes.
"""

from __future__ import print_function
import atexit
import collections
import signal
import time
import json


class Sampler(object):
    STACK_SEPARATOR = ";"
    """
    A simple stack sampler for low-overhead CPU profiling: samples the call
    stack every `interval` seconds and keeps track of counts by frame. Because
    this uses signals, it only works on the main thread.
    """
    def __init__(self, interval):
        self.interval = float(interval)
        self._started = None
        self._stack_counts = collections.defaultdict(int)

    def start(self):
        self._started = time.time()
        try:
            signal.signal(signal.SIGVTALRM, self._sample)
        except ValueError:
            raise ValueError('Can only sample on the main thread')

        signal.setitimer(signal.ITIMER_VIRTUAL, self.interval)
        atexit.register(self.stop)

    def _sample(self, signum, frame):
        stack = []
        while frame is not None:
            stack.append(self._format_frame(frame))
            frame = frame.f_back

        stack = Sampler.STACK_SEPARATOR.join(reversed(stack))
        self._stack_counts[stack] += 1
        signal.setitimer(signal.ITIMER_VIRTUAL, self.interval)

    def _format_frame(self, frame):
        return '{}({})'.format(frame.f_code.co_name,
                               frame.f_globals.get('__name__'))

    def output_stats(self):
        if self._started is None:
            return json.dumps({})
        elapsed = time.time() - self._started
        stats = {}
        stats['elapsed'] = elapsed
        stats['granularity'] = self.interval
        ordered_stacks = sorted(self._stack_counts.items(), key=lambda kv: kv[1], reverse=True)
        stats['stacks'] = [dict(frame=frame, count=count) for frame, count in ordered_stacks]
        return json.dumps(stats)

    def reset(self):
        self._started = time.time()
        self._stack_counts = collections.defaultdict(int)

    def stop(self):
        self.reset()
        signal.setitimer(signal.ITIMER_VIRTUAL, 0)

    def __del__(self):
        self.stop()


class ProfilingMiddleware(object):
    SECRET_HEADER_NAME = 'PROFILER_TOKEN'
    PROFILING_PATH = '/liveprofiler'

    def __init__(self, app, interval, secret_header):
        self.app = app
        self.secret_header = secret_header
        self.sampler = Sampler(interval)
        self.sampler.start()

    def __call__(self, environ, start_response):
        if environ.get('REQUEST_METHOD') != 'GET' or environ.get('PATH_INFO') != ProfilingMiddleware.PROFILING_PATH:
            return self.app(environ, start_response)

        if environ.get('HTTP_{}'.format(ProfilingMiddleware.SECRET_HEADER_NAME)) != self.secret_header:
            start_response('403 YOU SHALL NOT PASS!!!!!!!!!!!!1111oneoneonelephant', [])
            return []
        else:
            stats = self.sampler.output_stats()
            self.sampler.reset()
            start_response('200 OK', [])
            return [stats]

        return self.app(environ, start_response)
