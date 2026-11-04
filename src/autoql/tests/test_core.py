import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

from autoql.analysis_agent.evidence_registry import EvidenceRegistry
from autoql.query_agent.evaluator import location_points, enclosing, normalize_uri, Evaluator
from autoql.query_agent.graph import extract_query
from autoql.task_loader import safe_relative, load_task, select_project, UnsupportedInput
from autoql.prompt.codeql_template_prompt import supported_analysis_kinds, query_skeleton


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.root), *args]).decode().strip()
        git('init', '-q')
        git('config', 'user.email', 'tests@example.invalid')
        git('config', 'user.name', 'Tests')
        (self.root / 'a.java').write_bytes(b'first\r\nrepeat\r\nunique\r\nrepeat\r\nlast')
        git('add', 'a.java')
        git('commit', '-qm', 'test')
        sha = git('rev-parse', 'HEAD')
        self.registry = EvidenceRegistry(SimpleNamespace(repo_path=str(self.root),
            buggy_commit=sha, fix_commit=sha, output_dir=str(self.root / 'output')))

    def tearDown(self):
        self.temp.cleanup()

    def test_coordinates_and_repetition(self):
        result, last = self.registry.materialize([
            {'id': 'E1', 'revision': 'buggy', 'file': 'a.java',
             'start_line': 3, 'end_line': 3},
            {'id': 'E2', 'revision': 'buggy', 'file': 'a.java',
             'start_line': 5, 'end_line': 5},
        ])
        self.assertEqual((result['start_line'], result['end_line']), (3, 3))
        self.assertEqual(result['code'], 'unique\r\n')
        self.assertEqual(last['code'], 'last')

    def test_fail_closed(self):
        invalid = [
            {'id': 'E1', 'revision': 'parent', 'file': 'a.java',
             'start_line': 1, 'end_line': 1},
            {'id': 'E1', 'revision': 'buggy', 'file': '../a.java',
             'start_line': 1, 'end_line': 1},
            {'id': 'E1', 'revision': 'buggy', 'file': 'a.java',
             'start_line': 9, 'end_line': 9},
        ]
        for location in invalid:
            with self.assertRaises((KeyError, ValueError)):
                self.registry.materialize([location])


class EvaluationTests(unittest.TestCase):
    @staticmethod
    def loc(path='module/src/Foo.java', line=15):
        return {'physicalLocation': {'artifactLocation': {'uri': path}, 'region': {'startLine': line}}}

    def test_mixed_and_multiple_runs(self):
        path = {'codeFlows': [{'threadFlows': [{'locations': [{'location': self.loc()}]}]}], 'locations': [self.loc(line=40)]}
        data = {'runs': [{'results': [path, {'locations': [self.loc(line=20)]}]}, {'results': [{'locations': [self.loc(line=30)]}]}]}
        points = list(location_points(data, '/repo'))
        self.assertEqual(len(points), 4)
        self.assertEqual({tuple(p['result_id']) for p in points}, {(0, 0), (0, 1), (1, 0)})
        self.assertEqual(points[0]['basis'], 'path')

    def test_path_and_function(self):
        self.assertEqual(normalize_uri('file:///repo/a/src/Foo.java', '/repo'), 'a/src/Foo.java')
        self.assertEqual(normalize_uri('a/src/Foo.java', '/repo', base_id='%SRCROOT%'), 'a/src/Foo.java')
        self.assertNotEqual(normalize_uri('a/src/Foo.java', '/repo'), normalize_uri('b/src/Foo.java', '/repo'))
        with self.assertRaises(ValueError):
            normalize_uri('file:///else/Foo.java', '/repo')
        methods = [{'file': 'a.java', 'start_line': 1, 'end_line': 40, 'method': 'outer'},
                   {'file': 'a.java', 'start_line': 10, 'end_line': 20, 'method': 'inner'}]
        self.assertEqual(enclosing({'file': 'a.java', 'line': 15}, methods)['method'], 'inner')

    def test_file_hit_does_not_substitute_for_function_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'fix_info.csv').write_text('cve_id,commit,file,class,method,method_start\ncase,old,module/src/Foo.java,Foo,target,10\n')
            (root / 'codeql-database.yml').write_text('sourceLocationPrefix: /repo\n')
            target = {'file': 'module/src/Foo.java', 'class_name': 'Foo', 'method': 'target',
                      'signature': 'target()', 'start_line': 10, 'end_line': 20}
            other = {**target, 'method': 'other', 'signature': 'other()', 'start_line': 30, 'end_line': 40}
            task = SimpleNamespace(dataset_dir=tmp, cve_id='case', buggy_commit='old',
                                   buggy_db_path=tmp, fixed_db_path=tmp)
            evaluator = Evaluator(task, [target, other], [target, other])
            data = {'runs': [{'results': [{'locations': [self.loc(line=35)]}]}]}
            evaluated = evaluator.evaluate(data, {'runs': [{'results': []}]})
            self.assertTrue(evaluated['buggy']['hit_file'])
            self.assertFalse(evaluated['buggy']['hit_function'])
            self.assertFalse(evaluated['verified'])
            # Any line within target works; no exact-line equality is required.
            data['runs'][0]['results'][0]['locations'] = [self.loc(line=18)]
            self.assertTrue(evaluator.evaluate(data, {'runs': [{'results': []}]})['verified'])


class InputTemplateTests(unittest.TestCase):
    def test_select_project_by_cve_or_commit(self):
        commit = 'a' * 40
        rows = [{'cve_id': 'CVE-2022-25842', 'fix_commit_ids': commit}]
        self.assertEqual(select_project(rows, commit=commit)[0], rows[0])
        row, selected = select_project(rows, cve='cve-2022-25842')
        self.assertEqual(row, rows[0])
        self.assertIsNone(selected)
        with self.assertRaises(UnsupportedInput):
            select_project(rows, commit=commit, cve='CVE-2022-25842')
        with self.assertRaises(UnsupportedInput):
            select_project(rows, cve='not-a-cve')

    def test_dataset_requires_unique_exact_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / 'autoql_data'
            dataset.mkdir()
            table = dataset / 'project_info.csv'
            commit = 'a' * 40
            for rows in ('', commit + '\n' + commit + '\n'):
                table.write_text('fix_commit_ids\n' + rows)
                with self.assertRaises(UnsupportedInput):
                    load_task(commit, root, root / 'run')
                self.assertFalse((root / 'run').exists())

    def test_analysis_task_loading_does_not_require_databases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / 'autoql_data'
            repo = root / 'cves' / 'CVE-2022-25842' / 'example'
            dataset.mkdir()
            repo.mkdir(parents=True)

            def git(*args):
                return subprocess.check_output(
                    ['git', '-C', str(repo), *args], text=True).strip()

            git('init', '-q')
            git('config', 'user.email', 'tests@example.invalid')
            git('config', 'user.name', 'Tests')
            (repo / 'A.java').write_text('class A { void unsafe() {} }\n')
            git('add', 'A.java')
            git('commit', '-qm', 'buggy')
            buggy = git('rev-parse', 'HEAD')
            (repo / 'A.java').write_text('class A {}\n')
            git('commit', '-qam', 'fix')
            fixed = git('rev-parse', 'HEAD')
            (dataset / 'project_info.csv').write_text(
                'cve_id,github_repository_name,buggy_commit_id,fix_commit_ids\n'
                f'CVE-2022-25842,example,{buggy},{fixed}\n')

            task = load_task(None, root, root / 'run', dataset,
                             cve='CVE-2022-25842')
            self.assertEqual(task.fix_commit, fixed)
            self.assertEqual(task.input_kind, 'cve')
            self.assertFalse(Path(task.buggy_db_path).exists())
            self.assertFalse(Path(task.fixed_db_path).exists())
            self.assertFalse((root / 'run' / 'vuln_spec.json').exists())

    def test_templates(self):
        for kind in supported_analysis_kinds():
            self.assertIn('使用 CodeQL 语法建模', query_skeleton(kind))
        with self.assertRaises(ValueError):
            query_skeleton('hybrid')

    def test_query_format(self):
        query = '/** @kind problem */\nimport java\nfrom Method m where m.fromSource() select m, "Test"'
        self.assertEqual(extract_query('query_code:\n```query\n' + query + '\n```').strip(), query)
        self.assertEqual(extract_query('```ql\n' + query + '\n```').strip(), query)
        with self.assertRaises(ValueError):
            extract_query('```ql\n' + query + '\n```\n```ql\n' + query + '\n```')
        with self.assertRaises(ValueError):
            extract_query('query_code: ```query {{model.sources}} ```')

    def test_path_input(self):
        for path in ['/etc/passwd', '../x', 'a/../../b', 'a\\b']:
            with self.assertRaises(ValueError):
                safe_relative(path)
        with self.assertRaises(ValueError):
            load_task('short-sha', Path('.'), Path('unused'))


if __name__ == '__main__':
    unittest.main()
