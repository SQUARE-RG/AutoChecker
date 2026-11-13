import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from autoql.query_agent.tools import RetrievalContext
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
                detail = tools['get_doc_detail']
                self.assertIn(
                    'predicate localFlow', detail.invoke({'query': 'localFlow'}))
                self.assertIn(
                    'has not been searched', detail.invoke({'query': 'flowStep'}))

                resumed = RetrievalContext(
                    out, Limits(), collection_names=['test_collection'])
                self.assertIn('Already cached', resumed.search('localFlow'))
                history = json.loads(resumed.summaries())
                self.assertEqual(history['query'], 'localFlow')
                self.assertIn('predicate localFlow', history['summary'])


if __name__ == '__main__':
    unittest.main()
