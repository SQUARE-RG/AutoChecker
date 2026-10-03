"""Synchronous, single-flight CodeQL process owner; no LSP initialization."""
import json
import os
import queue
import signal
import subprocess
import threading
import time
from pathlib import Path
from .models import QuickEvalError
from .transport import read_message, write_message


def seconds_left(deadline):
    left = deadline - time.monotonic()
    if left <= 0: raise QuickEvalError('timeout', 'Deadline exceeded')
    return left


def terminate(process):
    if process.poll() is None:
        try: os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError: pass
        try: process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            process.wait()


def cli_json(binary, args, deadline):
    seconds_left(deadline)
    try:
        p = subprocess.Popen([binary, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             start_new_session=True)
    except OSError as exc:
        raise QuickEvalError('server_error', str(exc)) from exc
    try:
        stdout, stderr = p.communicate(timeout=seconds_left(deadline))
        if p.returncode:
            raise QuickEvalError('server_error', stderr.decode('utf-8', 'replace')[-8000:], returncode=p.returncode)
        return json.loads(stdout)
    except subprocess.TimeoutExpired as exc:
        raise QuickEvalError('timeout', 'CodeQL CLI command timed out') from exc
    except (ValueError, UnicodeError) as exc:
        raise QuickEvalError('decode_error', 'Invalid CLI JSON: '+str(exc)) from exc
    finally:
        terminate(p)
        for pipe in (p.stdout, p.stderr): pipe.close()


class QueryServerClient:
    def __init__(self, config, log_path):
        self.config, self.log_path = config, Path(log_path)
        self.process = None
        self.reader = None
        self.messages = queue.Queue()
        self.sequence = 0
        self.registered = set()
        self.log = None
        self.send_lock = threading.Lock()
        self.active_id = None
        self.cancel_event = threading.Event()

    def start(self, deadline):
        if self.process is not None and self.process.poll() is None: return
        self.stop()
        ram = cli_json(self.config.codeql_binary,
                       ['resolve', 'ram', f'--ram={self.config.ram_mb}', '--format=json'], deadline)
        self.log = self.log_path.open('ab')
        try:
            self.process = subprocess.Popen([self.config.codeql_binary, 'execute', 'query-server2',
                f'--threads={self.config.threads}', *ram], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=self.log, start_new_session=True)
        except OSError as exc:
            self.stop(); raise QuickEvalError('server_error', str(exc)) from exc
        self.messages = queue.Queue()
        stream, messages = self.process.stdout, self.messages
        def read_loop():
            try:
                while True:
                    message = read_message(stream)
                    # Progress notifications are deliberately not queued unboundedly.
                    if 'id' in message: messages.put(message)
            except Exception as exc: messages.put(exc)
        self.reader = threading.Thread(target=read_loop, daemon=True, name='codeql-quick-eval-rpc')
        self.reader.start()
        self.registered = set()

    def _send(self, message):
        try:
            with self.send_lock: write_message(self.process.stdin, message)
        except (OSError, ValueError, AttributeError) as exc:
            raise QuickEvalError('server_error', 'Cannot write to Query Server') from exc

    def request(self, method, body, deadline):
        self.sequence += 1
        request_id = self.sequence
        self.active_id = request_id
        self.cancel_event.clear()
        self._send({'jsonrpc':'2.0', 'id':request_id, 'method':method,
                    'params':{'body':body, 'progressId':request_id}})
        cancel_status = None
        cancellation_deadline = None
        try:
            while True:
                now=time.monotonic()
                if cancel_status is None and (self.cancel_event.is_set() or now >= deadline):
                    cancel_status = 'cancelled' if self.cancel_event.is_set() else 'timeout'
                    self._send({'jsonrpc':'2.0', 'method':'$/cancelRequest', 'params':{'id':request_id}})
                    cancellation_deadline = now + self.config.cancel_grace_seconds
                if cancel_status and now >= cancellation_deadline:
                    self.stop()
                    raise QuickEvalError(cancel_status, 'Query cancelled; unresponsive server terminated')
                wait = min(0.1, max(0.001, (cancellation_deadline or deadline)-now))
                try: msg = self.messages.get(timeout=wait)
                except queue.Empty: continue
                if isinstance(msg, Exception):
                    self.stop(); raise QuickEvalError(cancel_status or 'server_error', 'Query Server stream failed: '+str(msg))
                if msg.get('id') != request_id:
                    self.stop(); raise QuickEvalError('server_error', 'Unexpected JSON-RPC response id')
                if cancel_status: raise QuickEvalError(cancel_status, 'Query request cancelled')
                if 'error' in msg:
                    raise QuickEvalError('server_error', 'JSON-RPC error', rpc_error=msg['error'])
                result = msg.get('result')
                if not isinstance(result, dict): raise QuickEvalError('server_error', 'Invalid RPC result')
                return result
        finally: self.active_id = None

    def evaluate(self, body, deadline):
        self.start(deadline)
        db = body['db']
        if db not in self.registered:
            result = self.request('evaluation/registerDatabases', {'databases':[db]}, deadline)
            if db not in result.get('registeredDatabases', []):
                raise QuickEvalError('server_error', 'Database registration not confirmed', response=result)
            self.registered.add(db)
        return self.request('evaluation/runQuery', body, deadline)

    def cancel(self):
        self.cancel_event.set()

    def stop(self):
        if self.process is not None:
            terminate(self.process)
            if self.reader and self.reader is not threading.current_thread(): self.reader.join(timeout=2)
            for pipe in (self.process.stdin, self.process.stdout):
                if pipe: pipe.close()
        if self.log: self.log.close()
        self.process = None
        self.reader = None
        self.log = None
        self.registered.clear()
