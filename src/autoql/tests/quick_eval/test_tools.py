import json
import unittest
from unittest.mock import Mock
from autoql.quick_eval.tools import create_quick_eval_tools,compact_json


class ToolTests(unittest.TestCase):
    def test_adapter_and_schema(self):
        s=Mock();s.config.max_tool_bytes=16384
        s.evaluate.return_value={'status':'ok','row_count':3}
        tools={t.name:t for t in create_quick_eval_tools(s)}
        output=tools['codeql_quick_evaluate'].invoke({'query_id':'q','expected_revision':'hash','database':'db',
            'target':{'kind':'symbol','qualified_name':'p','arity':1}})
        self.assertEqual(json.loads(output),s.evaluate.return_value)
        self.assertEqual(s.evaluate.call_args.args[0].target.qualified_name,'p')
        with self.assertRaises(ValueError):
            tools['codeql_quick_evaluate'].invoke({'query_id':'q','expected_revision':'hash','database':'db',
                'target':{'kind':'symbol','qualified_name':'p','text':'not allowed'}})

    def test_bounded_valid_json(self):
        raw={'status':'ok','artifact_id':'probe-1','result_sets':[{'rows':[['😀'*50000] for _ in range(100)],'next_cursor':'abc'}]}
        output=compact_json(raw,1024)
        self.assertLessEqual(len(output.encode()),1024)
        self.assertTrue(json.loads(output)['output_truncated'])
