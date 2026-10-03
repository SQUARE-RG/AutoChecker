"""Content-Length JSON-RPC framing, independent of subprocess management."""
import json

MAX_MESSAGE = 16 * 1024 * 1024


def read_message(stream):
    headers = {}
    total = 0
    while True:
        line = stream.readline(8193)
        if not line: raise EOFError('Query server closed stdout')
        total += len(line)
        if total > 8192: raise ValueError('Protocol headers too large')
        if line in (b'\r\n', b'\n'): break
        key, value = line.decode('ascii').split(':', 1)
        if key.lower() in headers: raise ValueError('Duplicate protocol header')
        headers[key.lower()] = value.strip()
    size = int(headers['content-length'])
    if not 0 < size <= MAX_MESSAGE: raise ValueError('Invalid message length')
    data = bytearray()
    while len(data) < size:
        part = stream.read(size - len(data))
        if not part: raise EOFError('Truncated protocol body')
        data.extend(part)
    value = json.loads(data)
    if not isinstance(value, dict) or value.get('jsonrpc') != '2.0':
        raise ValueError('Invalid JSON-RPC message')
    return value


def write_message(stream, message):
    data = json.dumps(message, ensure_ascii=False, allow_nan=False).encode('utf-8')
    stream.write(f'Content-Length: {len(data)}\r\n\r\n'.encode('ascii') + data)
    stream.flush()
