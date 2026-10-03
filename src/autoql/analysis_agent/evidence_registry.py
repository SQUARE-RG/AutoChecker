"""The model selects text; immutable Git blobs determine all coordinates."""
from pathlib import Path
import hashlib
import json
import threading

from autoql.runtime import write_json
from autoql.task_loader import blob, safe_relative
from autoql.timing import timed


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

    @timed('analysis.capture_evidence')
    def capture(self, revision: str, file: str, snippet: str) -> dict:
        with self.lock:
            return self._capture(revision, file, snippet)

    def _capture(self, revision: str, file: str, snippet: str) -> dict:
        if revision not in ('buggy', 'fix'):
            return {'ok': False, 'error': 'INVALID_REVISION'}
        if not snippet or not snippet.strip():
            return {'ok': False, 'error': 'EMPTY_SNIPPET'}
        try:
            file = safe_relative(file)
            sha = self.task.buggy_commit if revision == 'buggy' else self.task.fix_commit
            raw = blob(Path(self.task.repo_path), sha, file)
            text = raw.decode('utf-8')
        except Exception:
            return {'ok': False, 'error': 'FILE_UNAVAILABLE_OR_UNSUPPORTED_ENCODING'}
        positions = []
        start = 0
        while (start := text.find(snippet, start)) >= 0:
            positions.append(start)
            start += 1
        if not positions:
            return {'ok': False, 'error': 'NOT_FOUND', 'hint': 'Copy original text, without display line numbers.'}
        if len(positions) != 1:
            return {'ok': False, 'error': 'AMBIGUOUS',
                    'candidate_lines': [text.count('\n', 0, p) + 1 for p in positions[:20]]}
        start = positions[0]
        end = start + len(snippet.rstrip('\r\n'))
        first = text.rfind('\n', 0, start) + 1
        last = text.find('\n', end)
        last = len(text) if last < 0 else last + 1
        entry = {'revision': revision, 'file': file, 'start_line': text.count('\n', 0, first) + 1,
                 'end_line': text.count('\n', 0, end) + 1, 'code': text[first:last]}
        for existing in self.entries.values():
            if all(existing[k] == v for k, v in entry.items()):
                return {'ok': True, 'evidence': existing}
        key = 'E' + str(len(self.entries) + 1)
        entry = {'id': key, **entry}
        self.entries[key] = entry
        self.blobs[key] = {'commit': sha, 'sha256': hashlib.sha256(raw).hexdigest()}
        write_json(Path(self.task.output_dir) / 'evidence_registry.json', self.entries)
        write_json(Path(self.task.output_dir) / 'evidence_blobs.json', self.blobs)
        return {'ok': True, 'evidence': entry}
