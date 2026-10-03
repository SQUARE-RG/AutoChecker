"""Opt in: QUICK_EVAL_INTEGRATION=1; creates its own tiny Java database."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from autoql.quick_eval import *
from autoql.quick_eval.selectors import resolve
from autoql.quick_eval.tools import create_quick_eval_tools


@unittest.skipUnless(os.environ.get('QUICK_EVAL_INTEGRATION')=='1','Set QUICK_EVAL_INTEGRATION=1 for real CLI tests')
class NativeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        existing=os.environ.get('QUICK_EVAL_EXISTING_FIXTURE')
        if existing:
            cls.temp=None
            cls.root=Path(existing).resolve()
            cls.pack=cls.root/'pack'
            cls.db=cls.root/'database'
            cls.connect_session()
            return
        output=os.environ.get('QUICK_EVAL_TEST_OUTPUT')
        cls.temp=None if output else tempfile.TemporaryDirectory(prefix='quick-eval-fixture-')
        cls.root=Path(output or cls.temp.name).resolve();cls.root.mkdir(parents=True,exist_ok=True)
        fixtures=Path(__file__).parent/'fixtures'
        cls.source=cls.root/'source';cls.source.mkdir()
        shutil.copyfile(fixtures/'Sample.java',cls.source/'Sample.java')
        cls.pack=cls.root/'pack';cls.pack.mkdir()
        for p in fixtures.glob('*.ql*'): shutil.copyfile(p,cls.pack/p.name)
        (cls.pack/'qlpack.yml').write_text('name: autoql/quick-eval-tests\nversion: 0.0.1\ndependencies:\n  codeql/java-all: "7.7.2"\n')
        def command(args):
            result=subprocess.run(['codeql',*args],capture_output=True,text=True,timeout=180)
            with (cls.root/'setup.log').open('a') as f: f.write(result.stdout+result.stderr)
            if result.returncode: raise RuntimeError(result.stderr)
        command(['pack','install',str(cls.pack)])
        cls.db=cls.root/'database'
        command(['database','create',str(cls.db),'--language=java','--build-mode=none','--source-root='+str(cls.source)])
        cls.connect_session()

    @classmethod
    def connect_session(cls):
        cls.s=QuickEvalSession(SessionConfig('codeql',str(cls.root/('session-'+__import__('uuid').uuid4().hex[:8])),[str(cls.pack)],{'fixture':str(cls.db)},
            max_requests=50,session_timeout_seconds=1200,request_timeout_seconds=120))
        cls.doc=cls.s.register_query(cls.pack/'example.ql')
        cls.lib=cls.s.register_query(cls.pack/'Context.qll')
        cls.context=cls.s.register_query(cls.pack/'context.ql')

    @classmethod
    def tearDownClass(cls):
        cls.s.close()
        if cls.temp: cls.temp.cleanup()

    def evaluate(self,target,doc=None,mode='sample',limit=50):
        d=doc or self.doc
        result=self.s.evaluate(EvaluationRequest(d.query_id,d.revision,'fixture',target,mode=mode,sample_limit=limit))
        self.assertEqual(result['status'],'ok',result)
        return result

    def values(self,result):
        # These fixtures use integer-derived QL entities, decoded as entity labels.
        def cell(value):
            return int(value['label']) if isinstance(value,dict) and set(value)=={'label'} else value
        return {tuple(cell(v) for v in row) for row in result['result_sets'][0]['rows']}

    def test_predicates_class_characteristic_member(self):
        for name,kind,arity,expected in [
            ('pair','predicate',2,{(1,2),(2,3),(3,4)}),
            ('successor','predicate',1,{(1,2),(2,3),(3,4)}),
            # functionB is evaluated as a declaration while calling functionA.
            ('functionB','predicate',1,{(1,22),(2,24),(3,26)}),
            ('Small','class',None,{(1,),(2,),(3,)}),
            ('Small::Small','characteristic',0,{(1,),(2,),(3,)}),
            ('Small::doubleValue','predicate',0,{(1,2),(2,4),(3,6)})]:
            with self.subTest(symbol=name):
                self.assertEqual(self.values(self.evaluate(SymbolTarget(name,arity,kind))),expected)

    def test_formula_expression_and_unicode_range(self):
        r=self.evaluate(SnippetTarget('pair(x, y) and y > 2'))
        self.assertEqual(self.values(r),{(2,3),(3,4)})
        r=self.evaluate(SnippetTarget('this * 2'))
        self.assertEqual(r['row_count'],3)


    def test_empty_count_and_page(self):
        self.assertEqual(self.evaluate(SymbolTarget('empty',1))['row_count'],0)
        self.assertEqual(self.evaluate(SymbolTarget('pair',2),mode='count')['row_count'],3)
        r=self.evaluate(SymbolTarget('pair',2),limit=1)
        rows=list(r['result_sets'][0]['rows']);cursor=r['result_sets'][0]['next_cursor']
        while cursor:
            page=self.s.read_results(r['artifact_id'],cursor)
            self.assertEqual(page['status'],'ok',page);rows+=page['rows'];cursor=page['next_cursor']
        self.assertEqual({tuple(x) for x in rows},{(1,2),(2,3),(3,4)})

    def test_library_query_context(self):
        direct=self.evaluate(SymbolTarget('Interesting',symbol_kind='class'),self.lib)
        contextual=self.evaluate(SymbolTarget('Interesting',symbol_kind='class',file_id=self.lib.file_id,
                                             expected_revision=self.lib.revision),self.context)
        self.assertEqual(direct['row_count'],0)
        self.assertEqual(self.values(contextual),{(2,)})

    def test_invalid_selection_then_recovery(self):
        r=self.s.evaluate(EvaluationRequest(self.doc.query_id,self.doc.revision,'fixture',SnippetTarget('import java')))
        self.assertNotEqual(r['status'],'ok');self.assertIsNone(r['row_count'])
        self.assertEqual(self.evaluate(SymbolTarget('pair',2))['row_count'],3)

    def test_real_tool_range_parity(self):
        rng,_=resolve((self.pack/'example.ql').read_text(),SymbolTarget('pair',2))
        direct=self.evaluate(RangeTarget(rng))
        tool=next(t for t in create_quick_eval_tools(self.s) if t.name=='codeql_quick_evaluate')
        r=json.loads(tool.invoke({'query_id':self.doc.query_id,'expected_revision':self.doc.revision,
            'database':'fixture','target':{'kind':'symbol','qualified_name':'pair','arity':2},'sample_limit':50}))
        self.assertEqual(r['status'],'ok',r)
        self.assertEqual(self.values(r),self.values(direct))

    def test_unicode_range_and_ambiguous_snippet(self):
        path=self.pack/'unicode.ql'
        path.write_bytes('import java\r\npredicate uni(int x) { /*😀中文*/ x = [1..2] }\r\nselect 1\r\n'.encode())
        doc=self.s.register_query(path)
        self.assertEqual(self.values(self.evaluate(SnippetTarget('x = [1..2]'),doc)),{(1,),(2,)})
        result=self.s.evaluate(EvaluationRequest(self.doc.query_id,self.doc.revision,'fixture',SnippetTarget('x + 1')))
        self.assertEqual(result['status'],'ambiguous_target')

    def test_native_timeout_and_recovery(self):
        # Warm the owned server, then cancel a newly compiled query (not startup).
        self.evaluate(SymbolTarget('pair',2))
        path=self.pack/'timeout.ql'
        path.write_text('import java\npredicate slow(int x, int y) { x=[1..1000000] and y=[1..1000000] }\nselect 1\n')
        doc=self.s.register_query(path)
        result=self.s.evaluate(EvaluationRequest(doc.query_id,doc.revision,'fixture',SymbolTarget('slow',2),timeout_seconds=.2))
        self.assertEqual(result['status'],'timeout',result)
        self.assertEqual(self.evaluate(SymbolTarget('pair',2))['row_count'],3)
