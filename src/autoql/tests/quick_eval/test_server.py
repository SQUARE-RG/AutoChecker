import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from autoql.quick_eval.models import SessionConfig,QuickEvalError
from autoql.quick_eval.server import QueryServerClient

FAKE = r'''
import sys,time,json
from autoql.quick_eval.transport import read_message,write_message
while True:
 m=read_message(sys.stdin.buffer)
 if m['method']=='$/cancelRequest':
  if mode=='cancel': write_message(sys.stdout.buffer,{'jsonrpc':'2.0','id':m['params']['id'],'result':{'resultType':4}})
  continue
 if mode=='eof': sys.exit(0)
 if mode=='stderr':
  sys.stderr.write('x'*100000);sys.stderr.flush()
 if mode in ('hang','cancel'): continue
 write_message(sys.stdout.buffer,{'jsonrpc':'2.0','method':'evaluation/progress','params':{'id':0}})
 write_message(sys.stdout.buffer,{'jsonrpc':'2.0','id':m['id']+(1 if mode=='wrongid' else 0),'result':{'resultType':0}})
'''


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.config=SessionConfig(sys.executable,str(self.root),[str(self.root)],{'db':'unused'},cancel_grace_seconds=.1)
        self.client=QueryServerClient(self.config,self.root/'stderr.log')
        import subprocess
        self.original_popen=subprocess.Popen
    def tearDown(self): self.client.stop();self.temp.cleanup()
    def start(self,mode):
        script=self.root/'fake.py';script.write_text('mode='+repr(mode)+'\n'+FAKE)
        def spawn(*args,**kwargs): return self.original_popen([sys.executable,str(script)],**kwargs)
        with patch('autoql.quick_eval.server.cli_json',return_value=[]),patch('autoql.quick_eval.server.subprocess.Popen',side_effect=spawn):
            self.client.start(time.monotonic()+2)
    def test_notifications_stderr_and_response(self):
        self.start('stderr')
        self.assertEqual(self.client.request('test',{},time.monotonic()+3),{'resultType':0})
        self.assertGreater((self.root/'stderr.log').stat().st_size,50000)
    def test_eof_and_bad_id(self):
        for mode in ('eof','wrongid'):
            self.start(mode)
            with self.assertRaises(QuickEvalError) as ctx: self.client.request('test',{},time.monotonic()+3)
            self.assertEqual(ctx.exception.status,'server_error')
    def test_hang_terminated_and_recovery(self):
        self.start('hang');process=self.client.process
        with self.assertRaises(QuickEvalError) as ctx: self.client.request('test',{},time.monotonic()+.15)
        self.assertEqual(ctx.exception.status,'timeout');self.assertIsNotNone(process.poll())
        self.start('normal')
        self.assertEqual(self.client.request('test',{},time.monotonic()+3)['resultType'],0)
    def test_explicit_cancel(self):
        self.start('cancel')
        timer=threading.Timer(.15,self.client.cancel);timer.start()
        try:
            with self.assertRaises(QuickEvalError) as ctx: self.client.request('test',{},time.monotonic()+3)
            self.assertEqual(ctx.exception.status,'cancelled')
        finally: timer.join()
    def test_close_idempotent(self):
        self.start('normal');process=self.client.process
        self.client.stop();self.client.stop()
        self.assertIsNotNone(process.poll())
