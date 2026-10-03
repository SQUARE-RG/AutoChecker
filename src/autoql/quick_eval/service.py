"""Independent native Quick Evaluation session. No AutoQL graph dependencies."""
import hashlib
import json
import math
import re
import shutil
import threading
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from .models import Document, EvaluationRequest, QuickEvalError, SourceRange
from .selectors import locate, resolve, protocol_position
from .server import QueryServerClient, cli_json, seconds_left
from .protocol import STATUS, compilation_target, position_encoding
from .results import ResultReader
from .artifacts import digest, write_json


class QuickEvalSession:
    def __init__(self, config):
        self.config=config
        executable=shutil.which(config.codeql_binary)
        if not executable: raise ValueError('CodeQL executable not found')
        config.codeql_binary=str(Path(executable).resolve())
        self.roots=[Path(p).resolve(strict=True) for p in config.allowed_roots]
        self.output=Path(config.artifact_dir).resolve()
        self.output.mkdir(parents=True,exist_ok=True)
        if (self.output/'session.json').exists():
            raise ValueError('artifact_dir already contains a session; use a fresh directory')
        self.start_time=time.monotonic()
        self.deadline=self.start_time+config.session_timeout_seconds
        self.requests=0
        self.documents={}
        self.cursors={}
        self.completed={}
        self.deleted_artifacts=[]
        self.lock=threading.Lock()
        self.closed=False
        self.version=None
        self.db_metadata={}
        for alias,path in config.databases.items():
            db=Path(path).resolve(strict=True)
            meta=db/'codeql-database.yml'
            text=meta.read_text()
            if not re.search(r'^finalised:\s*true\s*$',text,re.M):
                raise ValueError(f'Database not finalized: {alias}')
            revision=config.database_revisions.get(alias)
            if revision and not re.search(r'^\s+sha:\s*'+re.escape(revision)+r'\s*$',text,re.M):
                raise ValueError(f'Database revision mismatch: {alias}')
            config.databases[alias]=str(db)
            self.db_metadata[alias]=digest(meta)
        self.server=QueryServerClient(config,self.output/'server.stderr.log')
        self.reader=ResultReader(config.codeql_binary)
        self._manifest()

    def __enter__(self): return self
    def __exit__(self,*args): self.close()

    def _manifest(self):
        write_json(self.output/'session.json',{'config':asdict(self.config),'cli':self.version,
            'requests_reserved':self.requests,'closed':self.closed,'deleted_artifacts':self.deleted_artifacts,
            'database_metadata_hashes':self.db_metadata,
            'documents':[asdict(d) for d in self.documents.values()],
            'elapsed_seconds':time.monotonic()-self.start_time})

    def _active(self):
        if self.closed: raise QuickEvalError('invalid_request','Session is closed')
        if time.monotonic()>=self.deadline: raise QuickEvalError('budget_exhausted','Session deadline exceeded')

    def _allowed(self,path):
        path=Path(path).resolve(strict=True)
        if not any(path.is_relative_to(root) for root in self.roots):
            raise QuickEvalError('invalid_request','File is outside registered roots')
        if path.suffix not in ('.ql','.qll'): raise QuickEvalError('invalid_request','Expected .ql or .qll')
        return path

    def register_query(self,path):
        if not self.lock.acquire(blocking=False): raise QuickEvalError('busy','Session is running')
        try:
            self._active()
            p=self._allowed(path)
            identifier=hashlib.sha256(str(p).encode()).hexdigest()[:20]
            doc=Document(identifier,identifier,str(p),digest(p))
            self.documents[identifier]=doc
            self._manifest()
            return doc
        finally: self.lock.release()

    def _document(self,identifier,revision):
        doc=self.documents.get(identifier)
        if doc is None: raise QuickEvalError('invalid_request','Unknown document ID')
        self._allowed(doc.path)
        if revision!=doc.revision or digest(doc.path)!=revision:
            raise QuickEvalError('stale_revision','Document changed; register the new revision')
        return doc

    def locate_targets(self,query_id,expected_revision,name_filter=None):
        if not self.lock.acquire(blocking=False): return {'status':'busy'}
        try:
            self._active()
            doc=self._document(query_id,expected_revision)
            targets=locate(Path(doc.path).read_bytes().decode('utf-8'))
            for t in targets:
                t['target_id']=hashlib.sha256((doc.revision+json.dumps(t,sort_keys=True)).encode()).hexdigest()[:20]
                t['file_id']=doc.file_id
                t['expected_revision']=doc.revision
            return {'status':'ok','query_revision':doc.revision,
                    'targets':[t for t in targets if not name_filter or name_filter in t['qualified_name']]}
        except QuickEvalError as exc: return self._error(exc)
        except (OSError,UnicodeError) as exc: return self._error(QuickEvalError('invalid_request',str(exc)))
        finally: self.lock.release()

    def _snapshot(self):
        files={}
        for root in self.roots:
            for p in root.rglob('*'):
                if p.is_file() and (p.suffix in ('.ql','.qll') or p.name in ('qlpack.yml','codeql-pack.lock.yml','codeql-workspace.yml')):
                    if not p.resolve().is_relative_to(root):
                        raise QuickEvalError('invalid_request','Managed QL symlink escapes root')
                    files[str(p)]=digest(p)
        return files

    @staticmethod
    def _error(exc):
        return {'status':exc.status,'row_count':None,'result_sets':[],
                'diagnostics':[{'message':str(exc),**exc.details}]}

    def evaluate(self,request: EvaluationRequest):
        if not self.lock.acquire(blocking=False): return self._error(QuickEvalError('busy','Session is running'))
        began=time.monotonic()
        probe=None
        result=None
        try:
            self._active()
            if request.mode not in ('sample','count'): raise QuickEvalError('invalid_request','Invalid mode')
            if isinstance(request.sample_limit,bool) or not isinstance(request.sample_limit,int) or not 1<=request.sample_limit<=self.config.max_page_rows:
                raise QuickEvalError('invalid_request','Invalid sample_limit')
            if isinstance(request.timeout_seconds,bool) or not isinstance(request.timeout_seconds,(int,float)) or not math.isfinite(request.timeout_seconds) or request.timeout_seconds<=0:
                raise QuickEvalError('invalid_request','Invalid timeout')
            deadline=min(self.deadline,began+min(request.timeout_seconds,self.config.request_timeout_seconds))
            entry=self._document(request.query_id,request.expected_revision)
            target=request.target
            target_id=target.file_id or entry.file_id
            target_revision=target.expected_revision or (entry.revision if target_id==entry.file_id else None)
            doc=self._document(target_id,target_revision)
            if request.database not in self.config.databases: raise QuickEvalError('invalid_request','Unknown database alias')
            meta=Path(self.config.databases[request.database])/'codeql-database.yml'
            if digest(meta)!=self.db_metadata[request.database]: raise QuickEvalError('stale_revision','Database metadata changed')
            text=Path(doc.path).read_bytes().decode('utf-8')
            selected,resolved=resolve(text,target)
            if self.version is None:
                self.version=cli_json(self.config.codeql_binary,['version','--format=json'],deadline)
                # Resolution is recorded for reproducibility; no pack installation is performed.
                packs=cli_json(self.config.codeql_binary,['resolve','qlpacks','--format=json'],deadline)
                write_json(self.output/'resolved-packs.json',packs)
                self._manifest()
            encoding=position_encoding(self.version.get('version'),self.config.position_encoding)
            position=protocol_position(text,selected,doc.path,encoding=encoding)
            snapshot=self._snapshot()
            seconds_left(deadline)
            if self.requests>=self.config.max_requests: raise QuickEvalError('budget_exhausted','Request budget exhausted')
            self.requests+=1
            probe=f'probe-{self.requests:04d}'
            folder=self.output/'probes'/probe
            folder.mkdir(parents=True)
            body={'db':self.config.databases[request.database],'queryPath':entry.path,
                  'outputPath':str(folder/'results.bqrs'),'additionalPacks':self.config.additional_packs,
                  'externalInputs':{},'singletonExternalInputs':{},
                  'target':compilation_target(position,request.mode=='count')}
            if self.config.extension_packs: body['extensionPacks']=self.config.extension_packs
            write_json(folder/'request.json',{'status':'started','request':asdict(request),
                'resolved_target':resolved,'position':position,'position_encoding':encoding,
                'managed_files':snapshot,'protocol_body':body})
            self._manifest()
            backend_start=time.monotonic()
            raw=self.server.evaluate(body,deadline)
            backend_wall=time.monotonic()-backend_start
            write_json(folder/'protocol_result.json',raw)
            status=STATUS.get(raw.get('resultType'),'evaluation_error')
            result={'status':status,'artifact_id':probe,'query_revision':entry.revision,
                    'database':request.database,'resolved_target':{**resolved,'range':asdict(selected)},
                    'row_count':None,'result_sets':[],
                    'timing':{'backend_wall_ms':round(backend_wall*1000),
                              'backend_evaluation_time_raw':raw.get('evaluationTime')},
                    'diagnostics':[],'backend_result_type':raw.get('resultType')}
            if status!='ok': result['diagnostics']=[{'message':raw.get('message','Unknown backend failure')}]
            else:
                bqrs=folder/'results.bqrs'
                if not bqrs.is_file(): raise QuickEvalError('decode_error','Successful RPC did not produce BQRS')
                try: sets=self.reader.read(bqrs,request.sample_limit,request.mode,deadline)
                except QuickEvalError as exc:
                    if exc.status not in ('timeout','budget_exhausted'): exc.status='decode_error'
                    raise
                result['result_sets']=sets
                if len(sets)==1: result['row_count']=sets[0]['row_count']
                for s in sets:
                    nxt=s.pop('_next_offset',None)
                    s['first_cursor']=self._cursor(probe,s['name'],None,request.sample_limit) if request.mode=='sample' else None
                    s['next_cursor']=self._cursor(probe,s['name'],nxt,request.sample_limit) if nxt is not None and s['truncated'] else None
            if snapshot!=self._snapshot() or digest(meta)!=self.db_metadata[request.database]:
                raise QuickEvalError('stale_revision','Managed files or database metadata changed during evaluation')
            seconds_left(deadline)
            if status=='ok': self.completed[probe]=result
        except QuickEvalError as exc: result=self._error(exc)
        except (OSError,UnicodeError,ValueError,TypeError,AttributeError) as exc:
            result=self._error(QuickEvalError('invalid_request',str(exc)))
        finally:
            try:
                if result is not None:
                    result.setdefault('query_revision',request.expected_revision)
                    result.setdefault('database',request.database)
                    result.setdefault('mode',request.mode)
                    result.setdefault('timing',{})['wall_ms']=round((time.monotonic()-began)*1000)
                    if probe:
                        result['artifact_id']=probe
                        folder=self.output/'probes'/probe
                        write_json(folder/'summary.json',result)
                        write_json(folder/'diagnostics.json',result.get('diagnostics',[]))
                        record=json.loads((folder/'request.json').read_text())
                        record['status']='completed' if result['status']=='ok' else 'failed'
                        write_json(folder/'request.json',record)
                self._manifest()
            finally: self.lock.release()
        return result

    def _cursor(self,probe,name,offset,size):
        cursor=uuid.uuid4().hex
        self.cursors[cursor]=(probe,name,offset,size)
        return cursor

    def read_results(self,artifact_id,cursor):
        if not self.lock.acquire(blocking=False): return {'status':'busy'}
        try:
            self._active()
            if artifact_id not in self.completed or cursor not in self.cursors:
                raise QuickEvalError('invalid_request','Unknown completed artifact or cursor')
            probe,name,offset,size=self.cursors[cursor]
            if probe!=artifact_id: raise QuickEvalError('invalid_request','Cursor belongs to another artifact')
            deadline=min(self.deadline,time.monotonic()+self.config.request_timeout_seconds)
            page=self.reader.page(self.output/'probes'/probe/'results.bqrs',name,size,offset,deadline)
            from .artifacts import safe_numbers
            nxt=page.get('next')
            return {'status':'ok','artifact_id':probe,'historical_result':True,'result_set':name,
                    'rows':safe_numbers(page['tuples']),'columns':page.get('columns',[]),
                    'next_cursor':self._cursor(probe,name,nxt,size) if nxt is not None else None}
        except QuickEvalError as exc: return self._error(exc)
        except (OSError,ValueError,TypeError,KeyError) as exc: return self._error(QuickEvalError('decode_error',str(exc)))
        finally: self.lock.release()

    def delete_probe(self, artifact_id):
        """Explicitly remove this session's probe artifacts; never removes source/DB."""
        if not self.lock.acquire(blocking=False): return {'status':'busy'}
        try:
            self._active()
            if not isinstance(artifact_id,str) or not re.fullmatch(r'probe-\d{4,}',artifact_id):
                raise QuickEvalError('invalid_request','Invalid artifact ID')
            folder=self.output/'probes'/artifact_id
            if not (folder/'request.json').is_file():
                raise QuickEvalError('invalid_request','Unknown probe artifact')
            shutil.rmtree(folder)
            self.completed.pop(artifact_id,None)
            self.cursors={k:v for k,v in self.cursors.items() if v[0]!=artifact_id}
            self.deleted_artifacts.append(artifact_id)
            self._manifest()
            return {'status':'ok','deleted_artifact':artifact_id}
        except QuickEvalError as exc: return self._error(exc)
        finally: self.lock.release()

    def cancel(self): self.server.cancel()

    def close(self):
        self.cancel()
        with self.lock:
            if not self.closed:
                self.server.stop();self.closed=True;self._manifest()
