import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

from autoql import run_patch


class RunModeTests(unittest.TestCase):
    def test_analysis_mode_does_not_validate_or_open_databases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'run'
            task = SimpleNamespace(
                output_dir=str(output), workspace=str(output / 'workspace'),
                buggy_db_path='/missing/buggy', fixed_db_path='/missing/fixed',
                buggy_commit='a' * 40, fix_commit='b' * 40,
                cve_id='CVE-2022-25842', input_kind='cve',
                dataset_dir=str(root / 'data'), repo_path=str(root / 'repo'),
                fix_commit_message='fix', diff_path=str(output / 'patch.diff'))

            def load_task(*args, **kwargs):
                output.mkdir(parents=True)
                return task

            class FakeLLM:
                def __init__(self, *args):
                    pass
                def close(self):
                    pass

            class FakeAnalysis:
                def __init__(self, *args):
                    pass
                def run(self, additional_request=''):
                    return {
                        'vulnerability_summary': 'Unsafe operation.',
                        'evidence': [{
                            'id': 'E1', 'revision': 'buggy', 'file': 'A.java',
                            'start_line': 1, 'end_line': 1,
                            'code': 'unsafe();\n',
                        }],
                    }

            argv = [
                'autoql.run_patch', '--cve', 'CVE-2022-25842',
                '--run-mode', 'analysis', '--root', str(root),
                '--output', str(output),
            ]
            with (patch.object(sys, 'argv', argv),
                  patch('autoql.run_patch.load_task', side_effect=load_task),
                  patch('autoql.run_patch.validate_codeql_databases',
                        side_effect=AssertionError('analysis touched databases')),
                  patch('autoql.llm.StreamingLLM', FakeLLM),
                  patch('autoql.analysis_agent.agent.AnalysisAgent', FakeAnalysis),
                  patch('autoql.analysis_agent.evidence_registry.EvidenceRegistry',
                        lambda actual_task: object()),
                  patch('autoql.analysis_agent.vulnerability_metadata.load_vulnerability_metadata',
                        return_value=None)):
                self.assertEqual(run_patch.main(), 0)

            result = json.loads((output / 'result.json').read_text())
            self.assertEqual(result['final_status'], 'analysis_completed')
            self.assertFalse((output / 'preflight.json').exists())

    def test_full_mode_connects_analysis_preflight_and_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'run'
            calls = {'structure': [], 'query': 0}

            task = SimpleNamespace(
                output_dir=str(output), workspace=str(output / 'workspace'),
                buggy_db_path='/db/buggy', fixed_db_path='/db/fixed',
                buggy_commit='a' * 40, fix_commit='b' * 40,
                cve_id='CVE-2022-25842', input_kind='cve',
                dataset_dir=str(root / 'data'), repo_path=str(root / 'repo'),
                fix_commit_message='fix', diff_path=str(output / 'patch.diff'))

            def load_task(*args, **kwargs):
                output.mkdir(parents=True)
                return task

            class FakeCodeQL:
                def __init__(self, actual_output, limits, deadline):
                    self.java_pack = Path('/packs/java-all')
                def structure(self, database, side):
                    calls['structure'].append((database, side))
                    return [{'file': 'A.java', 'class_name': 'A',
                             'method': 'm', 'signature': 'm()',
                             'start_line': 1, 'end_line': 2}]

            class FakeEvaluator:
                granularity = 'function'
                mapping_unknown = False
                deleted = []
                def __init__(self, actual_task, buggy, fixed):
                    self.task = actual_task

            class FakeLLM:
                def __init__(self, *args):
                    pass
                def close(self):
                    pass

            spec = {
                'vulnerability_summary': 'Input reaches a sensitive operation.',
                'evidence': [{
                    'id': 'E1', 'revision': 'buggy', 'file': 'A.java',
                    'start_line': 1, 'end_line': 1, 'code': 'sink(input);\n',
                }],
            }

            class FakeAnalysis:
                def __init__(self, *args):
                    pass
                def run(self, additional_request=''):
                    return spec

            class FakeRetrieval:
                def __init__(self, actual_output, limits):
                    self.output = actual_output

            def run_query(actual_task, actual_spec, llm, retrieval,
                          codeql, evaluator, limits, initial):
                calls['query'] += 1
                self.assertEqual(actual_spec, spec)
                self.assertIsInstance(retrieval, FakeRetrieval)
                return {
                    'final_status': 'query_verified', 'route': 'finish',
                    'attempt': 1, 'final_query_path': str(output / 'final.ql'),
                }

            argv = [
                'autoql.run_patch', '--cve', 'CVE-2022-25842',
                '--run-mode', 'full', '--root', str(root),
                '--output', str(output),
            ]
            with (patch.object(sys, 'argv', argv),
                  patch('autoql.run_patch.load_task', side_effect=load_task),
                  patch('autoql.run_patch.validate_codeql_databases',
                        return_value=[{'side': 'buggy'}, {'side': 'fixed'}]),
                  patch('autoql.query_agent.codeql.CodeQL', FakeCodeQL),
                  patch('autoql.query_agent.evaluator.Evaluator', FakeEvaluator),
                  patch('autoql.llm.StreamingLLM', FakeLLM),
                  patch('autoql.analysis_agent.agent.AnalysisAgent', FakeAnalysis),
                  patch('autoql.analysis_agent.evidence_registry.EvidenceRegistry',
                        lambda actual_task: object()),
                  patch('autoql.analysis_agent.vulnerability_metadata.load_vulnerability_metadata',
                        return_value=None),
                  patch('autoql.query_agent.tools.RetrievalContext', FakeRetrieval),
                  patch('autoql.query_agent.graph.run_query', side_effect=run_query)):
                self.assertEqual(run_patch.main(), 0)

            self.assertEqual(calls['structure'], [
                ('/db/buggy', 'buggy'), ('/db/fixed', 'fixed')])
            self.assertEqual(calls['query'], 1)
            self.assertEqual(
                json.loads((output / 'result.json').read_text())['final_status'],
                'query_verified')
            self.assertEqual(
                json.loads((output / 'run_control.json').read_text())['run_mode'],
                'full')


if __name__ == '__main__':
    unittest.main()
