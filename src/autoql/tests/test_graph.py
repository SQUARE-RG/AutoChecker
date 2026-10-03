from pathlib import Path
import json
import tempfile
import time
from types import SimpleNamespace
import unittest

from langchain_core.messages import AIMessage
from autoql.runtime import Limits
from autoql.query_agent.graph import run_query
from autoql.query_agent.tools import RetrievalContext

QUERY = '''query_code:
```query
/** @name Test
 * @description Test query.
 * @kind problem
 * @problem.severity warning
 * @id autoql/test
 */
import java
from Method m where m.fromSource() select m, "Test"
```'''


class FakeLLM:
    deadline = time.time() + 60
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0
    def call(self, messages, tools, phase):
        self.calls += 1
        return next(self.responses)


class GraphTests(unittest.TestCase):
    def test_semantic_repair_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = SimpleNamespace(output_dir=tmp, buggy_commit='oldcommit',
                fix_commit='newcommit', cve_id='private-label',
                buggy_db_path='old', fixed_db_path='new')
            class Compiler:
                pack = root / 'ql'
                def compile(self, *args):
                    return {'returncode': 0, 'stderr': '', 'stdout': ''}
                def analyze(self, *args):
                    return {'runs': []}, {'returncode': 0}
            evaluation = {'verified': False, 'fixed_target_status': 'disappeared',
                'buggy': {'hit_function': False, 'num_results': 0},
                'fixed': {'num_results': 0}}
            llm = FakeLLM([AIMessage(content=QUERY)] * 4)
            state = run_query(task, {'analysis_kind': 'structural_pattern', 'evidence': [], 'model': {}},
                llm, RetrievalContext([], root, Limits()), Compiler(),
                SimpleNamespace(evaluate=lambda *args: evaluation, granularity='function'), Limits())
            self.assertEqual(state['final_status'], 'budget_exhausted')
            self.assertEqual(state['semantic_repairs'], 3)
            self.assertEqual(state['attempt'], 4)
            self.assertFalse((root / 'final.ql').exists())

    def test_database_failure_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = SimpleNamespace(output_dir=tmp, buggy_commit='oldcommit',
                fix_commit='newcommit', cve_id='private-label',
                buggy_db_path='old', fixed_db_path='new')
            class Compiler:
                pack = root / 'ql'
                def compile(self, *args):
                    return {'returncode': 0, 'stderr': '', 'stdout': ''}
                def analyze(self, *args):
                    raise RuntimeError('Database execution failed')
            def should_not_evaluate(*args):
                self.fail('Execution failure must not be evaluated as zero findings')
            with self.assertRaisesRegex(RuntimeError, 'Database execution failed'):
                run_query(task, {'analysis_kind': 'structural_pattern', 'evidence': [], 'model': {}},
                    FakeLLM([AIMessage(content=QUERY)]), RetrievalContext([], root, Limits()),
                    Compiler(), SimpleNamespace(evaluate=should_not_evaluate), Limits())
            self.assertFalse((root / 'final.ql').exists())

    def test_compile_repair_and_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = SimpleNamespace(output_dir=tmp, buggy_commit='oldcommit', fix_commit='newcommit',
                cve_id='private-label', buggy_db_path='old', fixed_db_path='new')
            class Compiler:
                pack = root / 'ql'
                calls = 0
                def compile(self, path, attempt):
                    self.calls += 1
                    return {'returncode': int(self.calls == 1), 'stderr': 'type error', 'stdout': ''}
                def analyze(self, *args):
                    return {'runs': []}, {'returncode': 0}
            evaluator = SimpleNamespace(evaluate=lambda *args: {'verified': True})
            llm = FakeLLM([AIMessage(content=QUERY), AIMessage(content=QUERY)])
            spec = {'analysis_kind': 'structural_pattern', 'evidence': [], 'model': {}}
            result = run_query(task, spec, llm, RetrievalContext([], root, Limits()), Compiler(), evaluator, Limits())
            self.assertEqual(result['final_status'], 'query_verified')
            self.assertEqual(result['compile_repairs'], 1)
            self.assertEqual(result['attempt'], 2)
            self.assertTrue((root / 'final.ql').exists())
            self.assertEqual(result['final_query_path'], str(root / 'final.ql'))
            self.assertEqual(result['feedback'], '')
            self.assertEqual(json.loads((root / 'attempts/1/vuln_spec.json').read_text()), spec)

    def test_parse_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = SimpleNamespace(output_dir=tmp)
            llm = FakeLLM([AIMessage(content='invalid'), AIMessage(content='invalid')])
            result = run_query(task, {'analysis_kind': 'structural_pattern'}, llm,
                RetrievalContext([], Path(tmp), Limits()), None, None, Limits())
            self.assertEqual(result['final_status'], 'budget_exhausted')
            self.assertEqual(llm.calls, 2)


if __name__ == '__main__':
    unittest.main()
