import tempfile
import unittest
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from autoql.query_agent.tools import EvidenceAstContext, RetrievalContext
from autoql.runtime import Limits


class RetrievalTests(unittest.TestCase):
    def test_dedup_cache_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            def backend(query, collections, top_k):
                self.assertEqual(collections, ['test_collection'])
                self.assertEqual(top_k, Limits().retrieval_top_k)
                if query == 'missing':
                    return []
                return [('chunk-1', 'predicate localFlow() { flowStep() }')]

            with patch('autoql.query_agent.tools._query_chroma', side_effect=backend):
                context = RetrievalContext(
                    out, Limits(), collection_names=['test_collection'])
                first = context.search('localFlow')
                self.assertIn('[doc chunk-1]', first)
                self.assertIn('predicate localFlow', first)
                duplicate = context.search(['flowStep'])
                self.assertIn('already retrieved by query "localFlow"', duplicate)
                self.assertIn('No matching', context.search('missing'))

                tools = {item.name: item for item in context.tools()}
                search = tools['search_docs']
                detail = tools['get_doc_detail']
                self.assertIn(
                    'Already cached',
                    search.invoke({'queries': ['localFlow']}))
                details = detail.invoke(
                    {'queries': ['localFlow', 'flowStep']})
                self.assertIn('predicate localFlow', details)
                self.assertIn('has not been searched', details)

                resumed = RetrievalContext(
                    out, Limits(), collection_names=['test_collection'])
                self.assertIn('Already cached', resumed.search('localFlow'))
                history = resumed.summaries()
                self.assertIn('query: "localFlow"', history)
                self.assertIn('answer: predicate localFlow', history)

    def test_evidence_ast_tool_uses_exact_id_and_caches_full_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'run'
            calls = []

            def extractor(run_dir, evidence_id, destination, **kwargs):
                calls.append((run_dir, evidence_id, destination, kwargs))
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(
                    f'Evidence AST: {evidence_id}\n'
                    'Mode: full\n└── [Method] unsafe\n',
                    encoding='utf-8')

            context = EvidenceAstContext(
                SimpleNamespace(output_dir=str(output)),
                {'evidence': [{
                    'id': 'E1', 'revision': 'buggy', 'file': 'A.java',
                    'start_line': 1, 'end_line': 2, 'code': 'unsafe();\n',
                }, {
                    'id': 'E2', 'revision': 'fix', 'file': 'A.java',
                    'start_line': 3, 'end_line': 4, 'code': 'safe();\n',
                }]},
                Limits(), extractor=extractor)
            ast_tool = {item.name: item for item in context.tools()}['get_evidence_ast']

            first = ast_tool.invoke({'evidence_ids': ['E1', 'E2']})
            second = ast_tool.invoke({'evidence_ids': ['E1', 'E2', 'E1']})
            self.assertEqual(first, second)
            self.assertIn('### Evidence: E1', first)
            self.assertIn('### Evidence: E2', first)
            self.assertIn('[Method] unsafe', first)
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][0], output)
            self.assertEqual(calls[0][1], 'E1')
            self.assertEqual(calls[0][3]['detail'], 'full')
            self.assertIn(
                'Available evidence IDs: E1, E2',
                ast_tool.invoke({'evidence_ids': ['E9']}))

    def test_evidence_ast_tool_reports_database_failure(self):
        def extractor(*args, **kwargs):
            raise ValueError('CodeQL returned no AST nodes')

        context = EvidenceAstContext(
            SimpleNamespace(output_dir='/unused'),
            {'evidence': [{'id': 'E1'}]}, Limits(), extractor=extractor)
        result = context.get('E1')
        self.assertIn('CodeQL AST unavailable for evidence E1', result)
        self.assertIn('CodeQL returned no AST nodes', result)


if __name__ == '__main__':
    unittest.main()
