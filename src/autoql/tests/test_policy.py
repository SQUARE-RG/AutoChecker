from types import SimpleNamespace
import unittest

from autoql.query_agent.policy import generation_issues
from autoql.query_agent.prompt_renderer import merge_evidence, render


class PolicyTests(unittest.TestCase):
    def test_renderer_accepts_analysis_v2_spec_without_template_mode(self):
        spec = {
            'vulnerability_summary': 'Request data reaches a file operation.',
            'evidence': [{
                'id': 'E1', 'revision': 'buggy', 'file': 'A.java',
                'start_line': 1, 'end_line': 1, 'code': 'unsafe(input);\n',
            }],
        }
        retrieval_history = (
            'query: "TaintTracking Global ConfigSig"\n'
            'answer: global taint tracking')
        messages = render(spec, '', '', retrieval_history)
        self.assertIn('class Source extends DataFlow::Node', messages[0].content)
        self.assertIn('# Tools Usage', messages[0].content)
        self.assertIn('get_doc_detail({"queries":', messages[0].content)
        self.assertIn('get_evidence_ast', messages[0].content)
        self.assertIn('{"status":"needs_evidence"', messages[0].content)
        self.assertIn('Request data reaches a file operation.', messages[1].content)
        self.assertIn('unsafe(input);', messages[1].content)
        self.assertIn('RETRIEVAL HISTORY', messages[1].content)
        self.assertIn('query and answer fields', messages[1].content)
        self.assertNotIn('ATTEMPT HISTORY', messages[1].content)
        self.assertIn('TaintTracking Global ConfigSig', messages[1].content)
        self.assertIn('QUERY GENERATION PHASE:\ninitial', messages[1].content)

        repaired = render(
            spec, 'current query', 'type error', retrieval_history,
            'compile_repair')
        self.assertIn('QUERY GENERATION PHASE:\ncompile_repair', repaired[1].content)
        self.assertNotIn('PHASE INSTRUCTIONS', repaired[1].content)
        self.assertNotIn('{"status":"needs_evidence"', repaired[0].content)
        self.assertNotIn('[AST node type derived from evidence]', repaired[0].content)
        self.assertIn('current query', repaired[1].content)
        self.assertIn('COMPILER DIAGNOSTICS:\ntype error', repaired[1].content)
        self.assertIn('type error', repaired[1].content)

        semantic = render(
            spec, 'current query', 'target verification failed',
            retrieval_history, 'semantic_repair')
        self.assertNotIn(
            '{"status":"needs_evidence"', semantic[0].content)
        self.assertNotIn('[AST node type derived from evidence]', semantic[0].content)

    def test_project_identity(self):
        spec = {'vulnerability_summary': 'Unsafe operation.',
                'evidence': [{'file': 'a.java', 'code': 'package app.impl;'}]}
        task = SimpleNamespace(buggy_commit='old', fix_commit='fixed', cve_id='private')
        self.assertTrue(generation_issues('m.hasQualifiedName("app.impl", "Helper")', spec, task))
        self.assertFalse(generation_issues('m.hasQualifiedName("java.io", "File")', spec, task))

    def test_overlap_union(self):
        first = {'id': 'E1', 'revision': 'buggy', 'file': 'a.java', 'start_line': 1, 'end_line': 2, 'code': 'a\nb\n'}
        second = {**first, 'id': 'E2', 'start_line': 2, 'end_line': 3, 'code': 'b\nc\n'}
        result = merge_evidence([second, first])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['code'], 'a\nb\nc\n')
        self.assertEqual(result[0]['evidence_ids'], ['E1', 'E2'])
        with self.assertRaises(ValueError):
            merge_evidence([first, {**second, 'code': 'x\nc\n'}])
