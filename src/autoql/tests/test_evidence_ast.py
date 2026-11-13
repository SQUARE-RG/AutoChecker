import tempfile
from pathlib import Path
import unittest

from autoql.evidence_ast import (
    build_ast_result,
    load_evidence,
    render_ast_text,
    render_compact_ast_text,
)


class EvidenceAstTests(unittest.TestCase):
    def test_load_evidence_selects_exact_id_and_validates_range(self):
        with tempfile.TemporaryDirectory() as raw:
            spec = Path(raw) / 'vuln_spec.json'
            spec.write_text(
                '{"evidence": ['
                '{"id":"E1","revision":"buggy","file":"src/A.java",'
                '"start_line":3,"end_line":5,"code":"x"},'
                '{"id":"E2","revision":"fix","file":"src/A.java",'
                '"start_line":8,"end_line":8,"code":"y"}]}'
            )
            evidence = load_evidence(spec, 'E1')
            self.assertEqual(evidence['file'], 'src/A.java')
            self.assertEqual(evidence['start_line'], 3)
            with self.assertRaisesRegex(ValueError, 'exactly one evidence'):
                load_evidence(spec, 'missing')

    def test_build_ast_result_preserves_unambiguous_tree(self):
        evidence = {
            'id': 'E1', 'revision': 'buggy', 'file': 'src/A.java',
            'start_line': 10, 'end_line': 12,
            'code': '  void f() {\n    sink();\n  }\n',
        }
        rows = [
            ['r0', '[Method] f', '/repo/src/A.java', 8, 3, 14, 4],
            ['r0/0', '(Parameters)', '', 0, 0, 0, 0],
            ['r0/1', '[MethodAccess] sink()', '/repo/src/A.java', 11, 5, 11, 10],
        ]
        result = build_ast_result(
            evidence, Path('/db'), 'a' * 40, 'buggy', rows,
            [['r0', 'r0/0', '0', 0], ['r0', 'r0/1', '1', 1]])
        self.assertEqual(result['ast']['roots'], ['r0'])
        self.assertEqual(result['ast']['nodes'][0]['scope'], 'container')
        self.assertEqual(result['ast']['nodes'][1]['scope'], 'synthetic')
        self.assertEqual(result['ast']['nodes'][2]['scope'], 'inside')
        self.assertEqual(result['stats']['edge_count'], 2)
        text = render_ast_text(result, 'full')
        self.assertIn('Evidence AST: E1', text)
        self.assertIn('└── [Method] f  @8:3-14:4', text)
        self.assertIn('├── (Parameters)  @<synthetic>', text)
        self.assertIn('└── [MethodAccess] sink()  @11:5-11:10', text)

    def test_compact_tree_collapses_ast_leaf_nodes(self):
        evidence = {
            'id': 'E1', 'revision': 'buggy', 'file': 'src/A.java',
            'start_line': 1, 'end_line': 3,
            'code': 'void f() {\n  sink(value);\n}\n',
        }
        rows = [
            ['r0', '[Method] f', '/repo/src/A.java', 1, 6, 1, 6],
            ['r0/0', '[BlockStmt] { ... }', '/repo/src/A.java', 1, 10, 3, 1],
            ['r0/0/0', '[ExprStmt] <Expr>;', '/repo/src/A.java', 2, 3, 2, 14],
            ['r0/0/0/0', '[MethodCall] sink(...)', '/repo/src/A.java', 2, 3, 2, 13],
            ['r0/0/0/0/0', '[VarAccess] value', '/repo/src/A.java', 2, 8, 2, 12],
        ]
        result = build_ast_result(
            evidence, Path('/db'), 'a' * 40, 'buggy', rows,
            [['r0', 'r0/0', '0', 0, ''], ['r0/0', 'r0/0/0', '0', 0, ''],
             ['r0/0/0', 'r0/0/0/0', '0', 0, ''],
             ['r0/0/0/0', 'r0/0/0/0/0', '0', 0, '']])
        text = render_compact_ast_text(result)
        self.assertIn('[Method] void f()  @1-3', text)
        self.assertIn('[Call] sink(value);', text)
        self.assertNotIn('BlockStmt', text)
        self.assertNotIn('VarAccess', text)

    def test_path_ids_keep_identical_synthetic_nodes_distinct(self):
        evidence = {
            'id': 'E1', 'revision': 'buggy', 'file': 'src/A.java',
            'start_line': 1, 'end_line': 2, 'code': '',
        }
        rows = [
            ['r0', '[Method] outer', '/repo/src/A.java', 1, 1, 1, 5],
            ['r0/4', '(Parameters)', '', 0, 0, 0, 0],
            ['r0/5', '[Method] lambda', '/repo/src/A.java', 2, 1, 2, 6],
            ['r0/5/4', '(Parameters)', '', 0, 0, 0, 0],
        ]
        edges = [
            ['r0', 'r0/4', '4', 4, ''],
            ['r0', 'r0/5', '5', 5, ''],
            ['r0/5', 'r0/5/4', '4', 4, ''],
        ]
        result = build_ast_result(
            evidence, Path('/db'), 'a' * 40, 'buggy', rows, edges)
        self.assertEqual(result['stats']['node_count'], 4)
        self.assertEqual(result['stats']['edge_count'], 3)
        self.assertEqual(result['ast']['roots'], ['r0'])
        self.assertIn('r0/4', result['ast']['nodes'][0]['children'])
        self.assertIn('r0/5/4', result['ast']['nodes'][2]['children'])


if __name__ == '__main__':
    unittest.main()
