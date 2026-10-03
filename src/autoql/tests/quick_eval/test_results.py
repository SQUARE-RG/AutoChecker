import unittest
from unittest.mock import patch
from autoql.quick_eval.results import ResultReader
from autoql.quick_eval.artifacts import safe_numbers
from autoql.quick_eval import QuickEvalError


class ResultTests(unittest.TestCase):
    def test_native_count_total_not_number_of_categories(self):
        r=ResultReader('codeql')
        with patch.object(r,'info',return_value={'result-sets':[{'name':'q','rows':2,'columns':[{'name':'Category'},{'name':'Count'}]}]}), patch.object(r,'page',return_value={'tuples':[['Total tuples',24],['Distinct values for "x"',12]]}):
            result=r.read('x',8,'count',100)
            self.assertEqual(result[0]['row_count'],24)
            self.assertEqual(result[0]['rows'],[])

    def test_unknown_count_shape(self):
        r=ResultReader('codeql')
        with patch.object(r,'info',return_value={'result-sets':[{'name':'q','rows':1,'columns':[{'name':'x'}]}]}),patch.object(r,'page',return_value={'tuples':[[1]]}):
            with self.assertRaises(QuickEvalError): r.read('x',8,'count',100)

    def test_multiple_sets_empty_and_paging(self):
        r=ResultReader('codeql')
        with patch.object(r,'info',return_value={'result-sets':[{'name':'a','rows':0,'columns':[]},{'name':'b','rows':4,'columns':[]}]}),patch.object(r,'page',side_effect=[{'tuples':[]},{'tuples':[[2]],'next':63}]):
            x=r.read('x',1,'sample',100)
            self.assertEqual(x[0]['row_count'],0)
            self.assertTrue(x[1]['truncated'])
            self.assertEqual(x[1]['_next_offset'],63)

    def test_large_int(self):
        self.assertEqual(safe_numbers([2**80,True])[0],{'kind':'integer','decimal':str(2**80)})

    def test_big_count_keeps_exact_total(self):
        r=ResultReader('codeql')
        with patch.object(r,'info',return_value={'result-sets':[{'name':'q','rows':1,'columns':[{'name':'Category'},{'name':'Count'}]}]}),patch.object(r,'page',return_value={'tuples':[['Total tuples',2**70]]}):
            self.assertEqual(r.read('x',8,'count',100)[0]['row_count'],2**70)
