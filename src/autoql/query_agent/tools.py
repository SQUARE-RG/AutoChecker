"""Stable retrieval cache over the installed official Java CodeQL library sources."""
from pathlib import Path
import re
import time
import math
import json
from collections import Counter

from langchain_core.tools import tool
from autoql.runtime import write_json


class RetrievalContext:
    def __init__(self, roots, output, limits):
        self.entries = {}
        self.output, self.limits = Path(output), limits
        cache = self.output / 'retrieval_cache.json'
        if cache.exists():
            self.entries = json.loads(cache.read_text())
        # Keep full cached snippets retrievable, but send repeated documents only
        # once during discovery, even when different terms return the same hit.
        self.document_queries = {}
        for query, answer in self.entries.items():
            for label in re.findall(r'^\[([^\n]+)\]$', answer, re.MULTILINE):
                if label != 'TRUNCATED':
                    self.document_queries.setdefault(label, query)
        self.documents = []
        for root in roots:
            root = Path(root)
            for path in sorted(root.rglob('*')):
                if path.suffix not in ('.qll', '.ql', '.md') or '.codeql' in path.parts:
                    continue
                text = path.read_text(errors='replace')
                lines = text.splitlines(keepends=True)
                for offset in range(0, len(lines), 70):
                    content = ''.join(lines[offset:offset + 90])
                    label = root.parent.name + '/' + str(path.relative_to(root)) + f':{offset + 1}'
                    tokens = self.tokens(label + '\n' + content)
                    self.documents.append((label, content, Counter(tokens)))
        self.df = Counter()
        for _, _, counts in self.documents:
            self.df.update(counts.keys())

    @staticmethod
    def tokens(text):
        split = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        raw = re.findall(r'[a-zA-Z_][a-zA-Z_0-9]*', text.lower())
        return raw + re.findall(r'[a-zA-Z_][a-zA-Z_0-9]*', split.lower())

    def search(self, queries):
        if isinstance(queries, str):
            queries = [queries]
        if not isinstance(queries, list) or len(queries) > self.limits.search_queries_per_call:
            return 'At most three search terms per call.'
        sections = []
        started = time.monotonic()
        for query in queries:
            if query in self.entries:
                sections.append(f'{query}: cached; use get_doc_detail with this exact query.')
                continue
            terms = set(self.tokens(query))
            scores = []
            for label, content, counts in self.documents:
                if time.monotonic() - started > self.limits.retrieval_timeout_seconds:
                    return 'Retrieval timeout; previous cached entries remain available.'
                score = sum(math.log(1 + len(self.documents) / (1 + self.df[t])) *
                            min(counts[t], 3) for t in terms if counts[t])
                if score:
                    scores.append((score, label, content))
            hits = sorted(scores, reverse=True)[:self.limits.retrieval_top_k]
            answer = '\n\n'.join(f'[{label}]\n' + content[:self.limits.document_max_chars] +
                ('\n[TRUNCATED]' if len(content) > self.limits.document_max_chars else '')
                for _, label, content in hits) or 'No matching official library documentation.'
            self.entries[query] = answer
            visible = []
            for _, label, content in hits:
                previous = self.document_queries.get(label)
                if previous is not None:
                    visible.append(f'[{label}] Already returned for {previous!r}; '
                                   'use get_doc_detail with that exact query.')
                else:
                    self.document_queries[label] = query
                    visible.append(f'[{label}]\n' + content[:self.limits.document_max_chars] +
                        ('\n[TRUNCATED]' if len(content) > self.limits.document_max_chars else ''))
            sections.append(query + '\n' + ('\n\n'.join(visible) if hits else answer))
        write_json(self.output / 'retrieval_cache.json', self.entries)
        return '\n\n'.join(sections)

    def summaries(self):
        return '\n'.join(q + ': ' + text[:160].replace('\n', ' ') for q, text in self.entries.items())

    def tools(self):
        @tool
        def search_docs(queries: str | list[str]) -> str:
            """Search installed official Java CodeQL API sources/examples using up to 3 terms."""
            return self.search(queries)

        @tool
        def get_doc_detail(query: str) -> str:
            """Retrieve a previous cached result by its exact original search query."""
            return self.entries.get(query, 'Unknown search key. Call search_docs first.')
        return [search_docs, get_doc_detail]
