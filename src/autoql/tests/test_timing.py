import json
from pathlib import Path
import tempfile
import unittest
from autoql.timing import TimingRecorder, CURRENT, timing_span


class TimingTests(unittest.TestCase):
    def test_nested_resume_and_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index in range(2):
                recorder = TimingRecorder()
                token = CURRENT.set(recorder)
                try:
                    with recorder.span('task.session', 'session'):
                        recorder.attach(tmp, resume=bool(index))
                        with timing_span('analysis', 'stage'):
                            with self.assertRaises(ValueError):
                                with timing_span('tool'):
                                    raise ValueError('test')
                finally:
                    CURRENT.reset(token)
                recorder.summarize('test_complete')
            data = json.loads((Path(tmp) / 'timing_summary.json').read_text())
            self.assertTrue(data['measurement_complete'])
            self.assertEqual(data['sessions'], 2)
            self.assertEqual(data['breakdown']['tool']['errors'], 2)
            self.assertGreaterEqual(data['wall_seconds'], data['measured_active_seconds'])
            self.assertGreaterEqual(data['breakdown']['analysis']['duration_seconds'], data['breakdown']['tool']['duration_seconds'])

    def test_legacy_resume_is_not_invented(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder = TimingRecorder()
            with recorder.span('task.session', 'session'):
                recorder.attach(tmp, resume=True)
            data = json.loads((Path(tmp) / 'timing_summary.json').read_text())
            self.assertFalse(data['measurement_complete'])
            self.assertIsNone(data['resume_gap_seconds'])

    def test_interrupted_session_stays_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder = TimingRecorder()
            recorder.attach(tmp)
            recorder.emit(dict(event='start', span_id='unfinished', category='session',
                name='task.session', timestamp=1, session_id='old', parent_id=None, metadata={}))
            resumed = TimingRecorder()
            with resumed.span('task.session', 'session'):
                resumed.attach(tmp, resume=True)
            data = json.loads((Path(tmp) / 'timing_summary.json').read_text())
            self.assertFalse(data['measurement_complete'])
            self.assertEqual(len(data['incomplete_spans']), 1)
            self.assertIsNone(data['resume_gap_seconds'])
