import io
import unittest
from autoql.quick_eval.transport import read_message,write_message


class Fragmented(io.BytesIO):
    def read(self,size=-1): return super().read(min(size,2))


class TransportTests(unittest.TestCase):
    def test_coalesced_unicode_and_fragmented(self):
        out=io.BytesIO()
        expected=[{'jsonrpc':'2.0','id':1,'result':{'s':'中文😀'}},
                  {'jsonrpc':'2.0','method':'progress','params':{}}]
        for v in expected: write_message(out,v)
        stream=Fragmented(out.getvalue())
        self.assertEqual([read_message(stream),read_message(stream)],expected)

    def test_invalid_or_truncated(self):
        for payload in [b'Content-Length: -1\r\n\r\n',b'Content-Length: 5\r\n\r\n{}',
                        b'Content-Length: 9999999999\r\n\r\n',b'Content-Length: 2\r\n\r\n[]']:
            with self.assertRaises((ValueError,EOFError)): read_message(io.BytesIO(payload))
