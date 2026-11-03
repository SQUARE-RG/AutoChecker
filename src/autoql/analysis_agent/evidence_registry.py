"""Materialize model-selected source coordinates from immutable Git blobs."""
from pathlib import Path
import hashlib
import json
import threading

from autoql.runtime import write_json
from autoql.task_loader import blob, safe_relative
from autoql.timing import timed


def raw_location(value):
    if hasattr(value, 'model_dump'):
        value = value.model_dump()
    return {key: value[key] for key in ('id', 'revision', 'file', 'start_line', 'end_line')}


def location_key(value):
    value = raw_location(value)
    return tuple(value[key] for key in ('id', 'revision', 'file', 'start_line', 'end_line'))


class EvidenceRegistry:
    def __init__(self, task):
        self.task = task
        self.lock = threading.RLock()
        self.entries = {}
        self.blobs = {}
        for name, attr in [('evidence_registry.json', 'entries'), ('evidence_blobs.json', 'blobs')]:
            path = Path(task.output_dir) / name
            if path.exists():
                setattr(self, attr, json.loads(path.read_text()))

    def _extract(self, location):
        location = raw_location(location)
        revision = location['revision']
        if revision not in ('buggy', 'fix'):
            raise ValueError('Evidence revision must be buggy or fix')
        file = safe_relative(location['file'])
        start, end = location['start_line'], location['end_line']
        if start < 1 or end < start:
            raise ValueError('Invalid evidence line range')

        sha = self.task.buggy_commit if revision == 'buggy' else self.task.fix_commit
        raw = blob(Path(self.task.repo_path), sha, file)
        text = raw.decode('utf-8')
        lines = text.splitlines(keepends=True)
        if end > len(lines):
            raise ValueError(
                f"Evidence range {start}-{end} exceeds {file} line count {len(lines)}")
        code = ''.join(lines[start - 1:end])
        if not code:
            raise ValueError('Evidence range produced empty source text')
        entry = {**location, 'file': file, 'code': code}
        return entry, {'commit': sha, 'sha256': hashlib.sha256(raw).hexdigest()}

    @timed('analysis.extract_evidence')
    def materialize(self, locations):
        """Replace the registry only after every selected location is valid."""
        with self.lock:
            entries, blobs = {}, {}
            for location in locations:
                entry, metadata = self._extract(location)
                if entry['id'] in entries:
                    raise ValueError('Duplicate evidence id: ' + entry['id'])
                entries[entry['id']] = entry
                blobs[entry['id']] = metadata
            self.entries, self.blobs = entries, blobs
            write_json(Path(self.task.output_dir) / 'evidence_registry.json', entries)
            write_json(Path(self.task.output_dir) / 'evidence_blobs.json', blobs)
            return [entries[raw_location(location)['id']] for location in locations]
