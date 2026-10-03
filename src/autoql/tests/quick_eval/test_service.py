import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from autoql.quick_eval import *


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.pack=self.root/'pack';self.pack.mkdir()
        self.query=self.pack/'a.ql';self.query.write_text('predicate p(int x) {x=1}\nselect 1\n')
        self.db=self.root/'db';self.db.mkdir();(self.db/'codeql-database.yml').write_text('finalised: true\n')
        self.s=QuickEvalSession(SessionConfig(sys.executable,str(self.root/'out'),[str(self.pack)],{'db':str(self.db)}))
        self.d=self.s.register_query(self.query)
        self.s.version={'version':'test'}
    def tearDown(self): self.s.close();self.temp.cleanup()
    def req(self): return EvaluationRequest(self.d.query_id,self.d.revision,'db',SymbolTarget('p',1))

    def test_stale_no_execution(self):
        self.query.write_text('select 2')
        result=self.s.evaluate(self.req())
        self.assertEqual(result['status'],'stale_revision');self.assertEqual(self.s.requests,0)

    def test_compile_error_not_zero_and_next_probe(self):
        with patch.object(self.s.server,'evaluate',return_value={'resultType':2,'message':'bad type','evaluationTime':-1}):
            result=self.s.evaluate(self.req())
        self.assertEqual(result['status'],'compile_error');self.assertIsNone(result['row_count'])
        self.assertEqual(json.loads((self.root/'out/probes/probe-0001/request.json').read_text())['status'],'failed')
        with patch.object(self.s.server,'evaluate',return_value={'resultType':99}):
            result=self.s.evaluate(self.req())
        self.assertEqual(result['status'],'evaluation_error')

    def test_missing_bqrs(self):
        with patch.object(self.s.server,'evaluate',return_value={'resultType':0}):
            self.assertEqual(self.s.evaluate(self.req())['status'],'decode_error')

    def test_mutation_during_execution(self):
        def run(body,deadline):
            self.query.write_text('select 2');return {'resultType':2}
        with patch.object(self.s.server,'evaluate',side_effect=run):
            self.assertEqual(self.s.evaluate(self.req())['status'],'stale_revision')

    def test_busy_and_budget(self):
        self.s.lock.acquire()
        try: self.assertEqual(self.s.evaluate(self.req())['status'],'busy')
        finally: self.s.lock.release()
        self.s.requests=self.s.config.max_requests
        self.assertEqual(self.s.evaluate(self.req())['status'],'budget_exhausted')

    def test_root_boundary_and_close(self):
        p=self.root/'outside.ql';p.write_text('select 1')
        with self.assertRaises(QuickEvalError): self.s.register_query(p)
        self.s.close();self.s.close()
        self.assertEqual(self.s.evaluate(self.req())['status'],'invalid_request')

    def test_cursor_cannot_access_arbitrary_path(self):
        self.assertEqual(self.s.read_results('../x','../y')['status'],'invalid_request')

    def test_success_paging_and_artifact_state(self):
        def run(body,deadline):
            Path(body['outputPath']).write_bytes(b'fake')
            return {'resultType':0,'evaluationTime':5}
        sets=[{'name':'q','row_count':2,'columns':[{'name':'x','kind':'i'}],
               'rows':[[1]],'returned_rows':1,'truncated':True,'_next_offset':25}]
        with patch.object(self.s.server,'evaluate',side_effect=run),patch.object(self.s.reader,'read',return_value=sets):
            result=self.s.evaluate(self.req())
        self.assertEqual(result['status'],'ok')
        with patch.object(self.s.reader,'page',return_value={'tuples':[[2]]}):
            page=self.s.read_results(result['artifact_id'],result['result_sets'][0]['next_cursor'])
        self.assertEqual(page['rows'],[[2]])
        self.assertIsNone(page['next_cursor'])
        self.assertIsNotNone(result['result_sets'][0]['first_cursor'])
        record=json.loads((self.root/'out/probes/probe-0001/request.json').read_text())
        self.assertEqual(record['status'],'completed')

    def test_database_metadata_change(self):
        (self.db/'codeql-database.yml').write_text('finalised: true\nchanged: true\n')
        self.assertEqual(self.s.evaluate(self.req())['status'],'stale_revision')

    def test_different_file_requires_revision(self):
        lib=self.pack/'lib.qll';lib.write_text('predicate p(int x) {x=1}')
        doc=self.s.register_query(lib)
        request=EvaluationRequest(self.d.query_id,self.d.revision,'db',SymbolTarget('p',1,file_id=doc.file_id))
        self.assertEqual(self.s.evaluate(request)['status'],'stale_revision')

    def test_explicit_probe_cleanup(self):
        with patch.object(self.s.server,'evaluate',return_value={'resultType':2}):
            result=self.s.evaluate(self.req())
        self.assertEqual(self.s.delete_probe(result['artifact_id'])['status'],'ok')
        self.assertFalse((self.root/'out/probes'/result['artifact_id']).exists())
        self.assertTrue(self.query.exists())
        self.assertEqual(self.s.delete_probe('../pack')['status'],'invalid_request')
