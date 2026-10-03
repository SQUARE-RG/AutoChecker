"""Conservative declaration locator; CodeQL remains the semantic authority."""
import re
from dataclasses import asdict
from .models import QuickEvalError, SourceRange, RangeTarget, SnippetTarget, SymbolTarget

_TOKEN = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|[A-Za-z_][\w]*|::|[^\s]', re.UNICODE)


def line_starts(text):
    return [0] + [m.end() for m in re.finditer('\n', text)]


def offset(text, line, column):
    starts = line_starts(text)
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (line, column)) or not 1 <= line <= len(starts):
        raise QuickEvalError('invalid_request', 'Invalid line or column')
    start = starts[line - 1]
    end = text.find('\n', start)
    end = len(text) if end < 0 else end
    if end > start and text[end - 1] == '\r':
        end -= 1
    if not 1 <= column <= end - start + 1:
        raise QuickEvalError('invalid_request', 'Column outside line')
    return start + column - 1


def range_for(text, start, end):
    import bisect
    starts = line_starts(text)
    a, b = bisect.bisect_right(starts, start), bisect.bisect_right(starts, end)
    return SourceRange(a, start - starts[a - 1] + 1, b, end - starts[b - 1] + 1)


def protocol_position(text, selected, path, encoding="utf16"):
    a = offset(text, selected.start_line, selected.start_column)
    b = offset(text, selected.end_line, selected.end_column)
    if a >= b:
        raise QuickEvalError('invalid_request', 'Selection must be nonempty and ordered')
    if encoding == 'codepoint':
        return {'fileName':path, 'line':selected.start_line, 'endLine':selected.end_line,
                'column':selected.start_column, 'endColumn':selected.end_column}
    if encoding != 'utf16': raise QuickEvalError('invalid_request','Unknown position encoding')
    starts = line_starts(text)
    return {'fileName': path, 'line': selected.start_line, 'endLine': selected.end_line,
            'column': len(text[starts[selected.start_line-1]:a].encode('utf-16-le')) // 2 + 1,
            'endColumn': len(text[starts[selected.end_line-1]:b].encode('utf-16-le')) // 2 + 1}


def locate(text):
    # Tokens retain offsets. Comments and strings cannot masquerade as declarations.
    tokens = [(m.group(), m.start(), m.end()) for m in _TOKEN.finditer(text)
              if not m.group().startswith(('//', '/*', '"'))]
    values = [t[0] for t in tokens]
    pairs, stack = {}, []
    for i, v in enumerate(values):
        if v in ('(', '{', '['): stack.append((v, i))
        elif v in (')', '}', ']'):
            if not stack or stack[-1][0] != {')':'(', '}':'{', ']':'['}[v]:
                raise QuickEvalError('unsupported_selector', 'Unbalanced syntax; use a source range')
            _, j = stack.pop(); pairs[j] = i
    if stack:
        raise QuickEvalError('unsupported_selector', 'Unbalanced syntax; use a source range')
    scopes, result = [], []
    for i, v in enumerate(values):
        while scopes and i > scopes[-1][0]: scopes.pop()
        prefix = [s[1] for s in scopes if s[1]]
        if v in ('module', 'class') and i+1 < len(tokens) and re.fullmatch(r'[A-Za-z_]\w*', values[i+1]):
            j=i+2
            while j<len(tokens) and values[j] not in ('{',';','='): j+=1
            # Parameterized declarations need actual QL name resolution; exclude their contents.
            complex_decl = j < len(tokens) and '<' in values[i+2:j]
            if v == 'class' and not complex_decl and not any(s[2]=='unsupported' for s in scopes):
                result.append({'qualified_name':'::'.join(prefix+[values[i+1]]),'symbol_kind':'class',
                               'arity':None,'range':asdict(range_for(text,tokens[i+1][1],tokens[i+1][2]))})
            if j<len(tokens) and values[j]=='{' and j in pairs:
                scopes.append((pairs[j], values[i+1], 'unsupported' if complex_decl else v))
        if v != '(' or i == 0 or i not in pairs: continue
        end=pairs[i]
        if end+1>=len(tokens) or values[end+1] not in ('{',';'): continue
        if any(s[2]=='unsupported' for s in scopes): continue
        name=values[i-1]
        if not re.fullmatch(r'[a-zA-Z_]\w*',name) or name in ('exists','forall','forex','if','any','count','sum','min','max'): continue
        # Only at module/class top level, never nested in an executable predicate body.
        enclosing=[(a,b) for a,b in pairs.items() if values[a]=='{' and a<i<b]
        if len(enclosing)!=len(scopes): continue
        characteristic=bool(scopes and scopes[-1][2]=='class' and name==scopes[-1][1])
        if not characteristic:
            if i<2 or not re.fullmatch(r'[a-zA-Z_]\w*',values[i-2]): continue
            if not name[0].islower(): continue
        params=values[i+1:end]
        # Ordinary typed parameters only; predicate/module parameters are out of scope.
        chunks=[]; start=0
        for n,t in enumerate(params):
            if t==',': chunks.append(params[start:n]); start=n+1
        if params: chunks.append(params[start:])
        if any(len(c)<2 or any(t in ('(',')','<','>','{','}','/','=') for t in c) for c in chunks): continue
        kind='characteristic' if characteristic else 'predicate'
        result.append({'qualified_name':'::'.join(prefix+[name]),'symbol_kind':kind,'arity':len(chunks),
                       'range':asdict(range_for(text,tokens[i-1][1],tokens[i-1][2]))})
    return result


def resolve(text, target):
    if isinstance(target, RangeTarget): return target.range, {'kind':'range'}
    if isinstance(target, SnippetTarget):
        if not target.text: raise QuickEvalError('invalid_request','Empty snippet')
        matches=[]; pos=0
        while True:
            pos=text.find(target.text,pos)
            if pos<0: break
            matches.append(range_for(text,pos,pos+len(target.text)));pos+=1
        if not matches: raise QuickEvalError('target_not_found','Snippet not found')
        if len(matches)>1: raise QuickEvalError('ambiguous_target','Snippet occurs more than once',candidates=[asdict(x) for x in matches[:50]])
        return matches[0], {'kind':'snippet'}
    if isinstance(target, SymbolTarget):
        matches=[x for x in locate(text) if x['qualified_name']==target.qualified_name
                 and (target.arity is None or x['arity']==target.arity)
                 and (target.symbol_kind is None or x['symbol_kind']==target.symbol_kind)]
        if not matches: raise QuickEvalError('unsupported_selector','No supported declaration matches; use range/snippet')
        if len(matches)>1: raise QuickEvalError('ambiguous_target','Multiple declarations match',candidates=matches)
        return SourceRange(**matches[0]['range']), {'kind':'symbol',**matches[0]}
    raise QuickEvalError('invalid_request','Unknown target selector')
