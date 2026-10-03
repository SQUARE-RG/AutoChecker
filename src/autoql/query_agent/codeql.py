"""Program-owned CodeQL execution and extraction. Queries never execute shell."""
import csv
import json
from pathlib import Path
import subprocess
import os
import signal

from autoql.runtime import command, remaining, write_json, write_text
from autoql.timing import timed


STRUCTURE_QUERY = '''import java
from Callable c
where c.fromSource()
select c.getFile().getRelativePath() as file,
       c.getDeclaringType().getName() as class_name,
       c.getName() as method,
       c.getSignature() as signature,
       c.getLocation().getStartLine() as start_line,
       c.getBody().getLocation().getEndLine() as end_line
'''


class CodeQL:
    def __init__(self, output, limits, deadline):
        self.output, self.limits, self.deadline = Path(output), limits, deadline
        packs = json.loads(command(['codeql', 'resolve', 'qlpacks', '--format=json']))
        self.java_pack = Path(packs['codeql/java-all'][0])
        self.query_pack = Path(packs['codeql/java-queries'][0])
        self.pack = self.output / 'ql'
        write_text(self.pack / 'qlpack.yml', 'name: autoql/generated\nversion: 0.0.1\ndependencies:\n  codeql/java-all: "' + self.java_pack.name + '"\n')
        self.run(['codeql', 'pack', 'install', str(self.pack)], 'pack-install', 120, strict=True)

    @timed(lambda self, args, label, *a, **kw: 'codeql.' + label)
    def run(self, args, label, timeout, strict=False):
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=remaining(self.deadline, timeout))
        except BaseException:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            write_json(self.output / 'codeql_logs' / (label + '.json'),
                {'returncode': process.returncode, 'stdout': stdout, 'stderr': stderr, 'interrupted': True})
            raise
        value = {'returncode': process.returncode, 'stdout': stdout, 'stderr': stderr}
        write_json(self.output / 'codeql_logs' / (label + '.json'), value)
        if strict and process.returncode:
            raise RuntimeError('CodeQL infrastructure/extraction failure: ' + stderr[-5000:])
        return value

    def compile(self, query, attempt):
        return self.run(['codeql', 'query', 'compile', '--check-only', '--threads=2', '--ram=4096', str(query)],
            f'compile-{attempt}', self.limits.compile_timeout_seconds)

    def analyze(self, db, query, side, attempt):
        sarif = self.output / 'attempts' / str(attempt) / f'{side}.sarif'
        result = self.run(['codeql', 'database', 'analyze', str(db), str(query),
            '--format=sarifv2.1.0', '--output=' + str(sarif), '--rerun', '--threads=2', '--ram=4096'],
            f'analyze-{attempt}-{side}', self.limits.database_run_timeout_seconds, strict=True)
        data = json.loads(sarif.read_text())
        if 'runs' not in data:
            raise ValueError('Invalid SARIF')
        return data, {'sarif': str(sarif), 'returncode': result['returncode']}

    def structure(self, db, side):
        query = self.pack / 'structure.ql'
        write_text(query, STRUCTURE_QUERY)
        bqrs = self.output / f'{side}-structure.bqrs'
        target = self.output / f'{side}-structure.csv'
        self.run(['codeql', 'query', 'run', str(query), '--database=' + str(db),
            '--output=' + str(bqrs), '--threads=2', '--ram=4096'],
            'structure-' + side, self.limits.database_run_timeout_seconds, strict=True)
        self.run(['codeql', 'bqrs', 'decode', str(bqrs), '--format=csv', '--output=' + str(target)],
            'structure-decode-' + side, 30, strict=True)
        with target.open() as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise ValueError('Database contains no extracted callable bodies')
        for row in rows:
            row['start_line'], row['end_line'] = int(row['start_line']), int(row['end_line'])
        return rows
