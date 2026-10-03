from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from pydantic import ValidationError

from autoql.analysis_agent.agent import ReadOnlySourceBackend
from autoql.analysis_agent.schemas import LocalDataFlowSpec, SPEC_SCHEMAS
from autoql.analysis_agent.spec_examples import SPEC_EXAMPLES
from autoql.analysis_agent.validator import SpecValidationError, finalize
from autoql.llm import TrackedChatModel
from langchain_core.messages import AIMessage, HumanMessage


class AnalysisTests(unittest.TestCase):
    def test_source_readonly_and_work_writable(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend = ReadOnlySourceBackend(root_dir=tmp, virtual_mode=True)
            self.assertIsNotNone(backend.write('/buggy/a.java', 'bad').error)
            self.assertIsNotNone(backend.edit('/fixed/a.java', 'a', 'b').error)
            self.assertIsNone(backend.write('/work/note.txt', 'notes').error)
            self.assertEqual((Path(tmp) / 'work/note.txt').read_text(), 'notes')
            with self.assertRaises(ValueError):
                backend.write('/work/../buggy/a.java', 'bad')

    def test_framework_model_uses_gateway(self):
        seen = []
        def call(messages, tools, phase):
            seen.append((messages, tools, phase))
            return AIMessage(content='complete')
        model = TrackedChatModel(gateway=SimpleNamespace(call=call))
        self.assertEqual(model.invoke([HumanMessage(content='x')]).content, 'complete')
        self.assertEqual(seen[0][2], 'analysis')

    def test_validator_rejects_fabricated_evidence(self):
        entry = {'description': 'input', 'expression': 'x', 'evidence_ids': ['E1']}
        raw = {'schema_version': '1.0', 'language': 'java', 'vulnerability_name': 'test',
               'vulnerability_summary': 'test mechanism', 'analysis_kind': 'taint_tracking',
               'evidence_ids': ['E1'], 'model': {'sources': [entry], 'sinks': [entry], 'barriers': [], 'additional_steps': []}}
        registry = SimpleNamespace(entries={'E1': {'id': 'E1', 'revision': 'buggy', 'code': 'actual x'}})
        self.assertEqual(finalize(raw, registry)['evidence'][0]['code'], 'actual x')
        raw['evidence_ids'] = ['E999']
        with self.assertRaises(SpecValidationError):
            finalize(raw, registry)

    def test_all_prompt_examples_are_schema_valid(self):
        self.assertEqual(set(SPEC_EXAMPLES), set(SPEC_SCHEMAS))
        for kind, example in SPEC_EXAMPLES.items():
            with self.subTest(kind=kind):
                SPEC_SCHEMAS[kind].model_validate(example)

    def test_local_flow_schema_rejects_string_scope_and_free_form_semantics(self):
        raw = dict(SPEC_EXAMPLES['local_data_flow'])
        raw['model'] = dict(raw['model'], scope='same method',
                            flow_semantics='value-preserving propagation')
        with self.assertRaises(ValidationError) as raised:
            LocalDataFlowSpec.model_validate(raw)
        paths = {tuple(error['loc']) for error in raised.exception.errors()}
        self.assertIn(('model', 'scope'), paths)
        self.assertIn(('model', 'flow_semantics'), paths)

    def test_validator_aggregates_semantic_issues(self):
        raw = dict(SPEC_EXAMPLES['local_data_flow'])
        raw['evidence_ids'] = ['E1', 'E999']
        raw['model'] = dict(raw['model'], targets=[])
        registry = SimpleNamespace(entries={
            'E1': {'id': 'E1', 'revision': 'fix', 'code': 'fixed source'}
        })
        with self.assertRaises(SpecValidationError) as raised:
            finalize(raw, registry)
        codes = {problem['code'] for problem in raised.exception.issues}
        self.assertEqual(
            {'unknown_evidence', 'empty_required_field', 'missing_buggy_evidence'}, codes)


if __name__ == '__main__':
    unittest.main()
