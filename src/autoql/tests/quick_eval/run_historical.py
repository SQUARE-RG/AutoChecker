"""Opt-in independent regression on the original run's databases. No LLM calls.

PYTHONPATH=src python -m autoql.tests.quick_eval.run_historical --output /tmp/qe-history
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from autoql.quick_eval import *
from autoql.quick_eval.tools import create_quick_eval_tools
from autoql.quick_eval.artifacts import write_json
from autoql.quick_eval.selectors import resolve


def run(output):
    root=Path(__file__).resolve().parents[4]
    corpus=root/'docs/quick_eval_test_cases/a0ab2fa9f492-20260918-035204'
    manifest=json.loads((corpus/'manifest.json').read_text())
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    pack=output/'pack';pack.mkdir()
    for n in ('candidate-1.ql','candidate-2.ql','structure.ql','qlpack.yml','codeql-pack.lock.yml'):
        shutil.copyfile(corpus/n,pack/n)
    for q in manifest['queries']:
        assert hashlib.sha256((pack/q['file']).read_bytes()).hexdigest()==q['sha256']
    config=SessionConfig('codeql',str(output/'session'),[str(pack)],
        {k:v['path'] for k,v in manifest['databases'].items()},
        database_revisions={k:v['revision'] for k,v in manifest['databases'].items()},
        max_requests=40,session_timeout_seconds=1800,request_timeout_seconds=180)
    observations=[]
    with QuickEvalSession(config) as s:
        docs=[s.register_query(pack/f'candidate-{i}.ql') for i in (1,2)]
        structure=s.register_query(pack/'structure.ql')
        text=(pack/'candidate-2.ql').read_text()
        lines=text.splitlines()
        span=lambda a,b:'\n'.join(lines[a-1:b]).removesuffix(' and').strip()
        probes=[('H01',docs[0],SymbolTarget('isOrigin',1)),
                ('H02',docs[1],SymbolTarget('isOrigin',1)),
                ('H03',docs[1],SymbolTarget('isTarget',1)),
                ('H05',docs[1],SnippetTarget('ma.getMethod().hasName("getName")')),
                ('H06',docs[1],SnippetTarget('cc.getArgument(1)')),
                ('H07',docs[1],SnippetTarget('n.asExpr() = cc.getArgument(1)')),
                ('H08',docs[1],SnippetTarget(span(18,22))),
                ('H09',docs[1],SnippetTarget(span(24,42))),
                ('H10',docs[1],SnippetTarget(span(72,73))),
                ('H11',docs[1],SnippetTarget(span(72,74))),
                ('H12',docs[1],SnippetTarget(span(72,75))),
                ('H13',structure,SnippetTarget('c.getSignature()'))]
        for side in ('buggy','fixed'):
            for name,doc,target in probes:
                r=s.evaluate(EvaluationRequest(doc.query_id,doc.revision,side,target,sample_limit=8,timeout_seconds=180))
                observations.append({'probe':name,'side':side,**r})
                print(json.dumps({'probe':name,'side':side,'status':r['status'],'rows':r['row_count'],'wall_ms':r['timing']['wall_ms']},ensure_ascii=False),flush=True)
                write_json(output/'observations.json',observations)
                expected='compile_error' if name=='H01' else 'ok'
                if r['status']!=expected:
                    raise AssertionError(f'{name}/{side}: {r}')
        # Same predicate through range, count, and real StructuredTool entry points.
        doc=docs[1]
        rng,_=resolve(text,SymbolTarget('isTarget',1))
        ranged=s.evaluate(EvaluationRequest(doc.query_id,doc.revision,'buggy',RangeTarget(rng),sample_limit=8))
        counted=s.evaluate(EvaluationRequest(doc.query_id,doc.revision,'buggy',SymbolTarget('isTarget',1),mode='count'))
        tool=next(t for t in create_quick_eval_tools(s) if t.name=='codeql_quick_evaluate')
        tooled=json.loads(tool.invoke({'query_id':doc.query_id,'expected_revision':doc.revision,'database':'buggy',
            'target':{'kind':'symbol','qualified_name':'isTarget','arity':1}}))
        baseline=next(r for r in observations if r['probe']=='H03' and r['side']=='buggy')
        for r in (ranged,counted,tooled):
            assert r['status']=='ok' and r['row_count']==baseline['row_count'],r
        assert ranged['result_sets'][0]['rows']==tooled['result_sets'][0]['rows']
        cursor=tooled['result_sets'][0]['next_cursor']
        page=s.read_results(tooled['artifact_id'],cursor)
        assert page['status']=='ok' and page['rows']
        write_json(output/'interface-parity.json',{'range':ranged,'count':counted,'tool':tooled,'next_page':page})
        # Compare cumulative relations after projection to common column identities.
        # H10 can be larger than samples: decode full BQRS for this independent oracle.
        from autoql.quick_eval.server import cli_json
        for side in ('buggy','fixed'):
            relations=[]
            for name in ('H10','H11','H12'):
                r=next(x for x in observations if x['probe']==name and x['side']==side)
                path=output/'session/probes'/r['artifact_id']/'results.bqrs'
                raw=cli_json(config.codeql_binary,['bqrs','decode',str(path),'--format=json','--entities=string,url'],s.deadline)
                data=next(iter(raw.values()));names=[c['name'] for c in data['columns']]
                indices=[names.index('origin'),names.index('target')]
                relations.append({json.dumps([row[i] for i in indices],sort_keys=True) for row in data['tuples']})
            assert relations[2]<=relations[1]<=relations[0]
        write_json(output/'summary.json',{'status':'passed','probes':len(observations),
            'historical_databases':config.databases,'interface_parity':True,'projection_subset_checks':True})
    run_full_baseline(output, config.databases)
    return output


def run_full_baseline(output, databases):
    """Independent full-query oracle, not a fallback for Quick Evaluation."""
    output=Path(output)
    counts={}
    for side,db in databases.items():
        sarif=output/f'full-{side}.sarif'
        proc=subprocess.run(['codeql','database','analyze',db,str(output/'pack/candidate-2.ql'),
            '--format=sarifv2.1.0','--output='+str(sarif),'--rerun','--threads=2','--ram=4096'],
            capture_output=True,text=True,timeout=180)
        write_json(output/f'full-{side}-log.json',{'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
        assert proc.returncode==0,proc.stderr
        data=json.loads(sarif.read_text())
        counts[side]=sum(len(run.get('results',[])) for run in data['runs'])
    assert counts=={'buggy':1,'fixed':0},counts
    write_json(output/'full-query-baseline.json',{'status':'passed','counts':counts})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    print(run(p.parse_args().output))
