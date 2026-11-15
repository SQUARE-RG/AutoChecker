from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

from autoql.query_agent.semantic_report import build_semantic_report


class SemanticReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.repo, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=self.repo, check=True)
        source = self.repo / 'src/Test.java'
        source.parent.mkdir()
        source.write_text('\n'.join(f'line {i}' for i in range(1, 21)) + '\n')
        subprocess.run(['git', 'add', '.'], cwd=self.repo, check=True)
        subprocess.run(['git', 'commit', '-qm', 'buggy'], cwd=self.repo, check=True)
        self.buggy = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=self.repo, text=True).strip()
        source.write_text('\n'.join(f'fixed line {i}' for i in range(1, 21)) + '\n')
        subprocess.run(['git', 'add', '.'], cwd=self.repo, check=True)
        subprocess.run(['git', 'commit', '-qm', 'fixed'], cwd=self.repo, check=True)
        self.fixed = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=self.repo, text=True).strip()
        self.task = SimpleNamespace(
            repo_path=str(self.repo), buggy_commit=self.buggy,
            fix_commit=self.fixed, buggy_db_path=self.root / 'missing-buggy-db',
            fixed_db_path=self.root / 'missing-fixed-db')

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def location(line, message=None):
        value = {'physicalLocation': {
            'artifactLocation': {'uri': 'src/Test.java'},
            'region': {'startLine': line}}}
        if message:
            value['message'] = {'text': message}
        return value

    def sarif(self, count=1, path=False):
        results = []
        for index in range(count):
            result = {
                'message': {'text': f'finding {index + 1}'},
                'locations': [self.location(10 + index)],
            }
            if path:
                result['codeFlows'] = [{'threadFlows': [{'locations': [
                    {'location': self.location(3, 'source')},
                    {'location': self.location(10 + index, 'sink')},
                ]}]}]
            results.append(result)
        return {'runs': [{'results': results}]}

    def test_report_contains_bounded_full_query_results_and_revision_sources(self):
        evaluation = {
            'buggy': {'hit_function': True},
            'fixed': {'hit_function': False},
        }
        report = build_semantic_report(
            self.task, self.sarif(7, path=True), self.sarif(1),
            evaluation, 'function')
        self.assertIn('Buggy database:\nTarget hit: true\nTotal results: 7', report)
        self.assertIn('showing 5 of 7', report)
        self.assertNotIn('Result 6:', report)
        self.assertIn('Location 2 (path start): src/Test.java:3', report)
        self.assertIn('line 10', report)
        self.assertIn('Fixed database:\nTarget hit: false\nTotal results: 1', report)
        self.assertIn('fixed line 10', report)

    def test_no_results_and_unsafe_locations_are_handled(self):
        unsafe = {'runs': [{'results': [{
            'message': {'text': 'outside'},
            'locations': [{'physicalLocation': {
                'artifactLocation': {'uri': '../secret'},
                'region': {'startLine': 1}}}],
        }]}]}
        evaluation = {
            'buggy': {'hit_file': False}, 'fixed': {'hit_file': False}}
        report = build_semantic_report(
            self.task, unsafe, {'runs': []}, evaluation, 'file')
        self.assertIn('Locations: (no safe physical location available)', report)
        self.assertIn('Fixed database:\nTarget hit: false\nTotal results: 0', report)
        self.assertIn('Returned result samples:\n(none)', report)


if __name__ == '__main__':
    unittest.main()
