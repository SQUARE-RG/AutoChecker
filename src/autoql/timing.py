"""Append-only nested timings; elapsed durations use a monotonic clock."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from pathlib import Path
import json
import os
import time
import uuid

from .runtime import write_json

CURRENT = ContextVar('autoql_timing', default=None)


class TimingRecorder:
    def __init__(self):
        self.events = []
        self.output = None
        self.session_id = uuid.uuid4().hex
        self.parents = ContextVar('timing_parents_' + self.session_id, default=())
        self.history_unknown = False

    def attach(self, output, resume=False):
        self.output = Path(output)
        path = self.output / 'timing_events.jsonl'
        previous = []
        if path.exists():
            previous = [json.loads(line) for line in path.read_text().splitlines() if line]
        self.history_unknown = resume and not previous
        summary = self.output / 'timing_summary.json'
        if resume and summary.exists():
            self.history_unknown |= json.loads(summary.read_text()).get('legacy_history_unknown', False)
        buffered, self.events = self.events, previous
        for event in buffered:
            self.emit(event)

    def emit(self, event):
        self.events.append(event)
        if self.output:
            with (self.output / 'timing_events.jsonl').open('a') as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + '\n')
                handle.flush()
                os.fsync(handle.fileno())

    @contextmanager
    def span(self, name, category='step', **metadata):
        wall, mono = time.time(), time.monotonic()
        identifier = uuid.uuid4().hex
        parents = self.parents.get()
        base = dict(span_id=identifier, session_id=self.session_id, name=name,
                    category=category, parent_id=parents[-1] if parents else None,
                    metadata=metadata)
        self.emit(dict(base, event='start', timestamp=wall))
        token = self.parents.set((*parents, identifier))
        status, error = 'success', None
        try:
            yield
        except BaseException as exc:
            status, error = 'error', type(exc).__name__
            raise
        finally:
            self.parents.reset(token)
            self.emit(dict(base, event='end', timestamp=time.time(),
                           duration_seconds=time.monotonic() - mono,
                           status=status, error_type=error))
            if self.output:
                self.summarize()

    def summarize(self, final_status=None):
        starts = {e['span_id']: e for e in self.events if e['event'] == 'start'}
        ends = {e['span_id']: e for e in self.events if e['event'] == 'end'}
        groups = {}
        for event in ends.values():
            group = groups.setdefault(event['name'], dict(category=event['category'],
                calls=0, duration_seconds=0, errors=0))
            group['calls'] += 1
            group['duration_seconds'] += event['duration_seconds']
            group['errors'] += event['status'] != 'success'
        sessions = [e for e in starts.values() if e['category'] == 'session']
        first = min((e['timestamp'] for e in sessions), default=time.time())
        last = max((ends[e['span_id']]['timestamp'] for e in sessions if e['span_id'] in ends), default=first)
        active = sum(ends[e['span_id']]['duration_seconds'] for e in sessions if e['span_id'] in ends)
        incomplete = [e for key, e in starts.items() if key not in ends]
        complete = not incomplete and not self.history_unknown
        write_json(self.output / 'timing_summary.json', dict(
            first_started_at=first, last_ended_at=last, final_status=final_status,
            wall_seconds=max(0, last - first), measured_active_seconds=active,
            resume_gap_seconds=max(0, last - first - active) if complete else None,
            measurement_complete=complete, legacy_history_unknown=self.history_unknown,
            incomplete_spans=incomplete, sessions=len(sessions), breakdown=groups,
            accounting='Inclusive nested spans: do not sum parents and children. Interrupted spans have unknown duration.'))


@contextmanager
def timing_span(name, category='step', **metadata):
    recorder = CURRENT.get()
    if recorder is None:
        yield
    else:
        with recorder.span(name, category, **metadata):
            yield


def timed(name, category='step'):
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            with timing_span(name(*args, **kwargs) if callable(name) else name, category):
                return fn(*args, **kwargs)
        return wrapped
    return decorate
