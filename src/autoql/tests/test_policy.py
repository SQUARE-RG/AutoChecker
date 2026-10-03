from types import SimpleNamespace
import unittest

from autoql.query_agent.policy import generation_issues
from autoql.query_agent.prompt_renderer import merge_evidence


class PolicyTests(unittest.TestCase):
    def test_project_identity_and_invented_guard(self):
        spec = {'evidence': [{'file': 'a.java', 'code': 'package app.impl;'}], 'model': {'barriers': []}}
        task = SimpleNamespace(buggy_commit='old', fix_commit='fixed', cve_id='private')
        self.assertTrue(generation_issues('m.hasQualifiedName("app.impl", "Helper")', spec, task))
        self.assertTrue(generation_issues('predicate isBarrier(Node n) { ... }', spec, task))
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
