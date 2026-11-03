from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

from pydantic import ValidationError

from autoql.analysis_agent.agent import AnalysisAgent, ReadOnlySourceBackend
from autoql.analysis_agent.evidence_registry import EvidenceRegistry
from autoql.analysis_agent.prompts import explorer_system_prompt
from autoql.analysis_agent.schemas import AnalysisBrief
from autoql.analysis_agent.validator import (SpecValidationError, finalize,
                                              validate_brief)
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

    def test_brief_rejects_model_generated_code_and_bad_range(self):
        base = {'id': 'E1', 'revision': 'buggy', 'file': 'A.java',
                'start_line': 1, 'end_line': 2}
        with self.assertRaises(ValidationError):
            AnalysisBrief.model_validate({
                'vulnerability_summary': 'summary',
                'evidence': [{**base, 'code': 'untrusted'}],
            })
        with self.assertRaises(ValidationError):
            AnalysisBrief.model_validate({
                'vulnerability_summary': 'summary',
                'evidence': [{**base, 'start_line': 3}],
            })

    def test_static_evidence_and_composer_constraints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, output = root / 'repo', root / 'output'
            repo.mkdir()
            output.mkdir()

            def git(*args):
                return subprocess.check_output(
                    ['git', '-C', str(repo), *args], text=True).strip()

            git('init', '-q')
            git('config', 'user.email', 'tests@example.invalid')
            git('config', 'user.name', 'Tests')
            (repo / 'A.java').write_text('class A {\n  void unsafe() {}\n}\n')
            git('add', 'A.java')
            git('commit', '-qm', 'buggy')
            buggy = git('rev-parse', 'HEAD')
            (repo / 'A.java').write_text('class A {\n}\n')
            git('commit', '-qam', 'fix')
            fixed = git('rev-parse', 'HEAD')

            task = SimpleNamespace(repo_path=str(repo), buggy_commit=buggy,
                                   fix_commit=fixed, output_dir=str(output))
            registry = EvidenceRegistry(task)
            raw = {
                'vulnerability_summary': 'An unsafe operation is removed by the fix.',
                'evidence': [
                    {'id': 'E1', 'revision': 'buggy', 'file': 'A.java',
                     'start_line': 1, 'end_line': 3},
                    {'id': 'E2', 'revision': 'fix', 'file': 'A.java',
                     'start_line': 1, 'end_line': 2},
                ],
            }
            brief = validate_brief(raw, registry)
            self.assertEqual(registry.entries['E1']['code'],
                             'class A {\n  void unsafe() {}\n}\n')
            spec = finalize(raw, brief, registry)
            self.assertEqual(set(spec), {'vulnerability_summary', 'evidence'})
            self.assertEqual([entry['id'] for entry in spec['evidence']], ['E1', 'E2'])

            changed = {**raw, 'evidence': [{**raw['evidence'][0], 'start_line': 2}]}
            with self.assertRaises(SpecValidationError):
                finalize(changed, brief, registry)
            invented = {**raw, 'evidence': [{
                'id': 'E9', 'revision': 'buggy', 'file': 'A.java',
                'start_line': 1, 'end_line': 1,
            }]}
            with self.assertRaises(SpecValidationError):
                finalize(invented, brief, registry)

    def test_explorer_prompt_is_task_independent(self):
        prompt = explorer_system_prompt()
        self.assertNotIn('CVE-', prompt)
        self.assertNotIn('fix_commit_message.txt', prompt)
        self.assertNotIn('analysis_kind', prompt)

        agent = AnalysisAgent.__new__(AnalysisAgent)
        agent.task = SimpleNamespace(fix_commit_message='update "quoted" version')
        request = agent._initial_request('')
        self.assertIn('update \\"quoted\\" version', request)
        self.assertNotIn('fix_commit_message.txt', request)


if __name__ == '__main__':
    unittest.main()
