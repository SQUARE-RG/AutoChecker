import tempfile
import unittest
from pathlib import Path

from autoql.query_agent.tools import RetrievalContext
from autoql.runtime import Limits


class RetrievalTests(unittest.TestCase):
    def test_dedup_cache_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'java' / 'lib'
            root.mkdir(parents=True)
            (root / 'Flow.qll').write_text('predicate localFlow() { flowStep() }\n')
            out = Path(tmp) / 'run'
            context = RetrievalContext([root], out, Limits())
            self.assertIn('predicate localFlow', context.search('localFlow'))
            self.assertIn('Already returned', context.search(['flowStep']))
            detail = {t.name: t for t in context.tools()}['get_doc_detail']
            self.assertIn('predicate localFlow', detail.invoke({'query': 'flowStep'}))
            resumed = RetrievalContext([root], out, Limits())
            self.assertIn('Already returned', resumed.search('predicate'))
            self.assertIn('cached', resumed.search('localFlow'))


if __name__ == '__main__':
    unittest.main()
