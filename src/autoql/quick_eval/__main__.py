"""Independent JSON CLI; never imports or runs the AutoQL generation graph."""
import argparse
import json
from dataclasses import asdict
from . import QuickEvalSession, SessionConfig, EvaluationRequest
from .models import target_from_dict


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',required=True,help='SessionConfig JSON file (fresh artifact_dir)')
    p.add_argument('--query',required=True)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--locate',action='store_true')
    g.add_argument('--request',help='JSON file: database, target, optional mode/sample_limit/timeout_seconds')
    args=p.parse_args()
    with open(args.config) as f: config=SessionConfig(**json.load(f))
    with QuickEvalSession(config) as session:
        doc=session.register_query(args.query)
        if args.locate: result=session.locate_targets(doc.query_id,doc.revision)
        else:
            with open(args.request) as f: request=json.load(f)
            request['target']=target_from_dict(request['target'])
            result=session.evaluate(EvaluationRequest(query_id=doc.query_id,expected_revision=doc.revision,**request))
        print(json.dumps({'document':asdict(doc),'result':result},ensure_ascii=False,indent=2))
        return 0 if result['status']=='ok' else 1


if __name__=='__main__': raise SystemExit(main())
