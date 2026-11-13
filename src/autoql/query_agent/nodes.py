"""Pure node operations used by the query orchestration graph."""
import re


def extract_query(text):
    # The label is preferred, but a single typed fenced block is equally
    # unambiguous. Normalize only the envelope; never repair generated QL here.
    matches = re.findall(r'```(?:query|ql|codeql)\s*([\s\S]*?)```', text)
    all_blocks = re.findall(r'```[^\n]*\n[\s\S]*?```', text)
    placeholders = (
        '{{', '[Vulnerability ', '[Description ', '[Numeric ',
        '[stable-query-id]', '[AST node ', '[Semantic ', '[Source ',
        '[Sensitive ', '[Sanitized ', '[Evidenced ', '[Alert ', '[doc ',
        '### Search:', 'Code Example', '**Type**', '**Path**',
    )
    if (len(matches) != 1 or len(all_blocks) != 1 or
            any(marker in matches[0] for marker in placeholders) or
            len(matches[0].strip()) < 50):
        raise ValueError('Return exactly one complete query_code: ```query block without placeholders.')
    query = matches[0].strip() + '\n'
    if not re.search(r'@kind\s+(?:path-problem|problem)\b', query) or 'select' not in query:
        raise ValueError('Missing query metadata or select')
    return query
