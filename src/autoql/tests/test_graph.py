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

NEEDS_EVIDENCE = '''```json
{"status":"needs_evidence","reason":"Add the buggy caller that supplies the sink argument."}
```'''


class FakeLLM:
    deadline = time.time() + 60
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0
        self.seen = []
    def call(self, messages, tools, phase):
        self.calls += 1
        self.seen.append(messages)
        return next(self.responses)


class GraphTests(unittest.TestCase):
    def test_initial_generation_can_request_evidence_without_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = SimpleNamespace(output_dir=tmp)
            result = run_query(
                task,
                {'vulnerability_summary': 'Unsafe operation.', 'evidence': []},
                FakeLLM([AIMessage(content=NEEDS_EVIDENCE)]),
                RetrievalContext(Path(tmp), Limits()), None, None, Limits())
            self.assertEqual(result['final_status'], 'needs_evidence')
            self.assertEqual(result['candidate_count'], 0)
            self.assertEqual(result['attempt'], 0)
            self.assertEqual(result['evidence_request']['status'],
                             'needs_evidence')
            self.assertIn('buggy caller', result['evidence_request']['reason'])

    def test_fourth_initial_evidence_request_is_not_forwarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = SimpleNamespace(output_dir=tmp)
            initial = {
                'candidate_count': 0, 'attempt': 0,
                'compile_repairs': 0, 'semantic_repairs': 0,
                'evidence_request_count': 3, 'history': [],
                'query_code': '', 'generation_phase': 'initial',
                'route': 'prep',
            }
            result = run_query(
                task,
                {'vulnerability_summary': 'Unsafe operation.', 'evidence': []},
                FakeLLM([AIMessage(content=NEEDS_EVIDENCE)]),
                RetrievalContext(Path(tmp), Limits()), None, None, Limits(),
                initial)
            self.assertEqual(result['final_status'], 'needs_review')
            self.assertEqual(result['candidate_count'], 0)
            self.assertNotIn('evidence_request', result)

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
            state = run_query(task, {'vulnerability_summary': 'Unsafe operation.', 'evidence': []},
                llm, RetrievalContext(root, Limits()), Compiler(),
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
                run_query(task, {'vulnerability_summary': 'Unsafe operation.', 'evidence': []},
                    FakeLLM([AIMessage(content=QUERY)]), RetrievalContext(root, Limits()),
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
                    return {
                        'returncode': int(self.calls == 1),
                        'stderr': 'type error',
                        'stdout': 'compiler note' if self.calls == 1 else '',
                    }
                def analyze(self, *args):
                    return {'runs': []}, {'returncode': 0}
            evaluator = SimpleNamespace(evaluate=lambda *args: {'verified': True})
            llm = FakeLLM([AIMessage(content=QUERY), AIMessage(content=QUERY)])
            spec = {'vulnerability_summary': 'Unsafe operation.', 'evidence': []}
            result = run_query(task, spec, llm, RetrievalContext(root, Limits()), Compiler(), evaluator, Limits())
            self.assertEqual(result['final_status'], 'query_verified')
            self.assertEqual(result['compile_repairs'], 1)
            self.assertEqual(result['attempt'], 2)
            self.assertTrue((root / 'final.ql').exists())
            self.assertEqual(result['final_query_path'], str(root / 'final.ql'))
            self.assertEqual(result['feedback'], '')
            self.assertEqual(json.loads((root / 'attempts/1/vuln_spec.json').read_text()), spec)
            repair_prompt = llm.seen[1][1].content
            self.assertIn(
                'COMPILER DIAGNOSTICS:\ntype error\n\ncompiler note',
                repair_prompt)
            self.assertNotIn('"returncode"', repair_prompt)

    def test_compile_repair_cannot_request_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = SimpleNamespace(
                output_dir=tmp, buggy_commit='oldcommit',
                fix_commit='newcommit', cve_id='private-label',
                buggy_db_path='old', fixed_db_path='new')

            class Compiler:
                pack = root / 'ql'
                calls = 0

                def compile(self, *args):
                    self.calls += 1
                    return {
                        'returncode': int(self.calls == 1),
                        'stderr': 'type error' if self.calls == 1 else '',
                        'stdout': '',
                    }

                def analyze(self, *args):
                    return {'runs': []}, {'returncode': 0}

            llm = FakeLLM([
                AIMessage(content=QUERY),
                AIMessage(content=NEEDS_EVIDENCE),
                AIMessage(content=QUERY),
            ])
            result = run_query(
                task,
                {'vulnerability_summary': 'Unsafe operation.', 'evidence': []},
                llm, RetrievalContext(root, Limits()), Compiler(),
                SimpleNamespace(evaluate=lambda *args: {'verified': True}),
                Limits())
            self.assertEqual(result['final_status'], 'query_verified')
            self.assertEqual(result['candidate_count'], 2)
            self.assertEqual(result['compile_repairs'], 1)
            self.assertEqual(result['evidence_request_count'], 0)
            self.assertIn(
                'needs_evidence is not allowed during compile_repair',
                llm.seen[2][-1].content)

    def test_parse_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = SimpleNamespace(output_dir=tmp)
            llm = FakeLLM([AIMessage(content='invalid'), AIMessage(content='invalid')])
            result = run_query(task, {'vulnerability_summary': 'Unsafe operation.', 'evidence': []}, llm,
                RetrievalContext(Path(tmp), Limits()), None, None, Limits())
            self.assertEqual(result['final_status'], 'budget_exhausted')
            self.assertEqual(llm.calls, 2)

    def test_semantic_repair_that_breaks_compilation_enters_compile_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = SimpleNamespace(
                output_dir=tmp, buggy_commit='oldcommit',
                fix_commit='newcommit', cve_id='private-label',
                buggy_db_path='old', fixed_db_path='new')

            class Compiler:
                pack = root / 'ql'
                calls = 0

                def compile(self, path, candidate):
                    self.calls += 1
                    return {
                        'returncode': int(self.calls == 2),
                        'stderr': 'type error' if self.calls == 2 else '',
                        'stdout': '',
                    }

                def analyze(self, *args):
                    return {'runs': []}, {'returncode': 0}

            evaluations = iter([
                {
                    'verified': False,
                    'fixed_target_status': 'disappeared',
                    'buggy': {'hit_function': False, 'num_results': 0},
                    'fixed': {'num_results': 0},
                },
                {'verified': True},
            ])
            evaluator = SimpleNamespace(
                evaluate=lambda *args: next(evaluations),
                granularity='function')
            llm = FakeLLM([AIMessage(content=QUERY)] * 3)
            compiler = Compiler()
            result = run_query(
                task,
                {'vulnerability_summary': 'Unsafe operation.', 'evidence': []},
                llm, RetrievalContext(root, Limits()), compiler, evaluator,
                Limits())

            self.assertEqual(result['final_status'], 'query_verified')
            self.assertEqual(result['candidate_count'], 3)
            self.assertEqual(result['attempt'], 3)
            self.assertEqual(result['semantic_repairs'], 1)
            self.assertEqual(result['compile_repairs'], 1)
            self.assertEqual(compiler.calls, 3)
            phases = [messages[1].content for messages in llm.seen]
            self.assertIn('QUERY GENERATION PHASE:\ninitial', phases[0])
            self.assertIn('QUERY GENERATION PHASE:\nsemantic_repair', phases[1])
            self.assertIn('QUERY GENERATION PHASE:\ncompile_repair', phases[2])


if __name__ == '__main__':
    unittest.main()
