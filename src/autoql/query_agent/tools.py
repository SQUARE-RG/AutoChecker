"""Run-scoped tools for CodeQL documentation and evidence AST inspection.

This follows the retrieval protocol used by ``src/codeql_agent/tools.py``:

* ``search_docs`` performs embedding retrieval across the language collections;
* results retain Chroma chunk IDs so repeated documents can be suppressed;
* prompts receive ``query``/``answer`` history entries with short answers; and
* ``get_doc_detail`` retrieves cached answers by exact original queries.

Unlike the standalone CodeQL agent, AutoQL persists the context so a resumed
run keeps the same retrieval history and document de-duplication state.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from langchain_core.tools import tool

from autoql.evidence_ast import extract_evidence_ast
from autoql.runtime import write_json


JAVA_DOC_COLLECTIONS = (
    'java_codeql_stdlib',
    'java_codeql_language_guides',
    'java_codeql_local_queries',
    'codeql_ql_reference',
)


def _query_chroma(query: str, collection_names: list[str], top_k: int):
    """Lazy import keeps module loading independent from the embedding stack."""
    from retriever.retriever_codeql_uniform import query_chroma_docs_with_ids
    return query_chroma_docs_with_ids(
        [query], collection_names, top_k=top_k)


def _make_summary(query: str, answer: str) -> str:
    clean = re.sub(r'\[doc [^\]]+\]', '', answer)
    return ' '.join(clean.split())[:120]


class RetrievalContext:
    """One AutoQL run's query-to-answer cache and Chroma chunk-ID history."""

    def __init__(self, output, limits, collection_names=None):
        self.output = Path(output)
        self.limits = limits
        self.collection_names = list(collection_names or JAVA_DOC_COLLECTIONS)
        self.cache_path = self.output / 'retrieval_cache.json'
        self.entries: dict[str, dict] = {}
        if self.cache_path.is_file():
            try:
                cached = json.loads(self.cache_path.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                cached = {}
            # Ignore caches from the previous local-keyword implementation.
            self.entries = {
                query: entry for query, entry in cached.items()
                if isinstance(query, str) and isinstance(entry, dict) and
                isinstance(entry.get('answer'), str) and
                isinstance(entry.get('doc_ids'), list) and
                isinstance(entry.get('summary'), str)
            }
            # Normalize old summary formats while preserving answers and chunk
            # IDs. Rendering adds explicit query/answer field labels.
            for query, entry in self.entries.items():
                entry['summary'] = _make_summary(query, entry['answer'])

    def _persist(self):
        write_json(self.cache_path, self.entries)

    def seen_doc_ids(self) -> set[str]:
        return {
            doc_id
            for entry in self.entries.values()
            for doc_id in entry['doc_ids']
        }

    def find_entry_with_ids(self, doc_ids) -> str | None:
        wanted = set(doc_ids)
        for query, entry in self.entries.items():
            if wanted.intersection(entry['doc_ids']):
                return query
        return None

    def summaries(self, limit: int = 8) -> str:
        selected = list(self.entries.items())[:limit]
        if not selected:
            return '(none; call search_docs when documentation is needed)'
        return '\n'.join(
            f'query: {json.dumps(query, ensure_ascii=False)}\n'
            f'answer: {entry["summary"]}'
            for query, entry in selected)

    def search(self, queries):
        if isinstance(queries, str):
            queries = [queries]
        if not isinstance(queries, list) or not all(
                isinstance(query, str) and query.strip() for query in queries):
            return 'queries must be a non-empty string or a list of non-empty strings.'
        if len(queries) > self.limits.search_queries_per_call:
            return (f'At most {self.limits.search_queries_per_call} search terms '
                    'may be submitted per call.')

        sections = []
        for raw_query in queries:
            query = raw_query.strip()
            if query in self.entries:
                sections.append(
                    f'### Search: {query}\nAlready cached. Use '
                    f'get_doc_detail(queries=[{json.dumps(query)}]) for the '
                    'stored result.')
                continue

            pairs = _query_chroma(
                query, self.collection_names, self.limits.retrieval_top_k)
            if not pairs:
                sections.append(
                    f'### Search: {query}\nNo matching CodeQL documentation.')
                continue

            seen = self.seen_doc_ids()
            new_pairs = [
                (str(chunk_id), text) for chunk_id, text in pairs
                if str(chunk_id) not in seen
            ]
            if not new_pairs:
                previous = self.find_entry_with_ids(
                    [str(chunk_id) for chunk_id, _ in pairs])
                detail = (f' Use get_doc_detail(queries=['
                          f'{json.dumps(previous)}]) to read it.'
                          if previous else '')
                sections.append(
                    f'### Search: {query}\nAll matching chunks were already '
                    f'retrieved by query "{previous}".{detail}')
                continue

            answer = '\n\n'.join(
                f'[doc {chunk_id}]\n{text[:self.limits.document_max_chars]}'
                for chunk_id, text in new_pairs)
            self.entries[query] = {
                'answer': answer,
                'doc_ids': [chunk_id for chunk_id, _ in new_pairs],
                'summary': _make_summary(query, answer),
            }
            sections.append(f'### Search: {query}\n{answer}')

        self._persist()
        return '\n\n'.join(sections) if sections else 'No search terms supplied.'

    def tools(self):
        @tool
        def search_docs(queries: str | list[str]) -> str:
            """Search the Java CodeQL ChromaDB collections.

            Pass up to the configured limit of concise English searches in one
            call. Use it for Java CodeQL APIs/signatures, existing source/sink
            models or official queries, and data-flow/query authoring guides.
            Example: {"queries": ["TaintTracking Global ConfigSig",
            "MethodCall getArgument"]}. Results are cached by the exact query;
            repeated Chroma chunks are not sent twice.
            """
            return self.search(queries)

        @tool
        def get_doc_detail(queries: str | list[str]) -> str:
            """Return full cached results for one or more earlier searches.

            Copy each ``query`` value from RETRIEVAL HISTORY exactly and pass
            it in ``queries``. Do not pass the answer text or paraphrase the
            query. Example: {"queries": ["asExpr", "localFlowStep"]}.
            """
            if isinstance(queries, str):
                queries = [queries]
            if not isinstance(queries, list) or not queries or not all(
                    isinstance(query, str) and query for query in queries):
                return ('queries must be a non-empty string or a list of '
                        'non-empty strings.')
            sections = []
            for query in dict.fromkeys(queries):
                entry = self.entries.get(query)
                if entry is None:
                    sections.append(
                        f'### Detail: {query}\nQuery has not been searched. '
                        f'Call search_docs(queries=[{json.dumps(query)}]) first.')
                else:
                    sections.append(f'### Detail: {query}\n{entry["answer"]}')
            return '\n\n'.join(sections)

        return [search_docs, get_doc_detail]


class EvidenceAstContext:
    """Expose complete CodeQL PrintAst text for registered vuln_spec evidence."""

    def __init__(self, task, spec, limits, extractor=None):
        self.task = task
        self.spec = spec
        self.limits = limits
        self.extractor = extractor or extract_evidence_ast
        self.output = Path(task.output_dir)
        self.evidence = {
            entry['id']: entry
            for entry in spec.get('evidence', [])
            if isinstance(entry, dict) and isinstance(entry.get('id'), str)
        }
        self.cache: dict[str, str] = {}

    def get(self, evidence_id: str) -> str:
        if not isinstance(evidence_id, str) or evidence_id not in self.evidence:
            available = ', '.join(sorted(self.evidence)) or '(none)'
            return (
                f'Unknown evidence_id {evidence_id!r}. '
                f'Available evidence IDs: {available}.')
        if evidence_id in self.cache:
            return self.cache[evidence_id]

        destination = self.output / 'evidence_ast' / f'{evidence_id}-full.txt'
        try:
            self.extractor(
                self.output, evidence_id, destination,
                timeout=self.limits.database_run_timeout_seconds,
                output_format='text', detail='full')
            text = destination.read_text(encoding='utf-8')
        except (ValueError, RuntimeError, OSError) as exc:
            return (
                f'CodeQL AST unavailable for evidence {evidence_id}: '
                f'{type(exc).__name__}: {exc}')
        self.cache[evidence_id] = text
        return text

    def tools(self):
        @tool
        def get_evidence_ast(evidence_ids: str | list[str]) -> str:
            """Return complete CodeQL Java PrintAst text for evidence items.

            Pass one or more exact IDs from VULNERABILITY SPEC, for example
            ``{"evidence_ids": ["E1", "E2"]}``. The tool automatically uses
            the buggy or fixed CodeQL database declared by each evidence item.
            Results are complete rather than relevance-pruned and may be large.
            """
            if isinstance(evidence_ids, str):
                evidence_ids = [evidence_ids]
            if not isinstance(evidence_ids, list) or not evidence_ids or not all(
                    isinstance(evidence_id, str) and evidence_id
                    for evidence_id in evidence_ids):
                return ('evidence_ids must be a non-empty string or a list of '
                        'non-empty strings.')
            return '\n\n'.join(
                f'### Evidence: {evidence_id}\n{self.get(evidence_id)}'
                for evidence_id in dict.fromkeys(evidence_ids))

        return [get_evidence_ast]
