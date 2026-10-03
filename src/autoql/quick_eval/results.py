from .server import cli_json
from .models import QuickEvalError
from .artifacts import safe_numbers


class ResultReader:
    def __init__(self, binary): self.binary = binary

    def info(self, path, deadline):
        return cli_json(self.binary,['bqrs','info',str(path),'--format=json'],deadline)

    def page(self, path, name, rows, offset, deadline):
        args=['bqrs','decode',str(path),'--format=json','--entities=string,url',
              '--result-set='+name,'--rows='+str(rows)]
        if offset is not None: args.append('--start-at='+str(offset))
        return cli_json(self.binary,args,deadline)

    def read(self, path, limit, mode, deadline):
        try:
            info=self.info(path,deadline)
            sets=info['result-sets']
            result=[]
            for entry in sets:
                page=self.page(path,entry['name'],limit if mode=='sample' else 100,None,deadline)
                rows=page['tuples']
                result.append({'name':entry['name'],'row_count':entry['rows'],
                    'columns':entry['columns'],'rows':rows if mode=='count' else safe_numbers(rows),
                    'returned_rows':len(rows),'truncated':len(rows)<entry['rows'],
                    '_next_offset':page.get('next')})
            if mode=='count':
                if len(result)!=1 or [c['name'] for c in result[0]['columns']] != ['Category','Count']:
                    raise QuickEvalError('decode_error','Unrecognized native count result shape')
                counts=result[0]['rows']
                totals=[row[1] for row in counts if len(row)==2 and row[0]=='Total tuples']
                if len(totals)!=1 or isinstance(totals[0],bool) or not isinstance(totals[0],int) or totals[0]<0:
                    raise QuickEvalError('decode_error','Unrecognized native count value')
                result[0].update(row_count=totals[0], count_details=safe_numbers(counts),
                                 count_details_truncated=result[0]['truncated'],
                                 columns=[],rows=[],returned_rows=0,
                                 truncated=False,_next_offset=None)
            return result
        except QuickEvalError: raise
        except (KeyError,TypeError,ValueError) as exc:
            raise QuickEvalError('decode_error','Unexpected BQRS structure: '+str(exc)) from exc
