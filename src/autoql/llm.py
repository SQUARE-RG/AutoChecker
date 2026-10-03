"""One streaming transport for both agents with per-physical-request accounting."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import uuid
import asyncio
import httpx
from contextvars import copy_context

from dotenv import load_dotenv
from langchain_core.messages import message_chunk_to_message, messages_to_dict
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ConfigDict
from typing import Any

from .runtime import BudgetExceeded, remaining, write_json
from .timing import timed, timing_span


class TransientLLMError(RuntimeError):
    pass


class RequestDeadlineExceeded(TimeoutError):
    """A total request deadline is not blindly retried as a network failure."""


class TrackedChatModel(BaseChatModel):
    """Framework-owned calls, including summarization, use the same audited transport."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    gateway: Any
    phase: str = 'analysis'

    @property
    def _llm_type(self):
        return 'autoql-streaming-shared-provider'

    def bind_tools(self, tools, **kwargs):
        return self.bind(tools=tools, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        message = self.gateway.call(messages, kwargs.get('tools', []), self.phase)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def get_num_tokens_from_messages(self, messages, tools=None):
        # Context sizing only, never billing; conservative character estimate.
        return sum(len(str(m.content)) // 2 + 16 for m in messages)


class StreamingLLM:
    def __init__(self, root: Path, output: Path, limits, deadline: float):
        load_dotenv(root / '.env')
        self.model_name = os.getenv('MODEL_NAME', 'deepseek')
        if 'deepseek' not in self.model_name:
            raise ValueError('Current shared model provider supports DeepSeek only')
        self.model = ChatOpenAI(model=self.model_name, temperature=0.7,
            api_key=os.environ['DEEPSEEK_API_KEY'],
            base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
            max_retries=0, timeout=httpx.Timeout(limits.llm_read_timeout_seconds,
                connect=limits.llm_connect_timeout_seconds, write=limits.llm_write_timeout_seconds,
                pool=limits.llm_pool_timeout_seconds),
            streaming=True, stream_usage=True)
        self.output, self.limits, self.deadline = output, limits, deadline
        self.counts = {'analysis': 0, 'query': 0}
        self.records = []
        if (output / 'budget.json').exists():
            saved = json.loads((output / 'budget.json').read_text())
            self.counts = saved['logical_calls']
            self.deadline = saved['deadline']
        if (output / 'usage.jsonl').exists():
            self.records = [json.loads(line) for line in (output / 'usage.jsonl').read_text().splitlines() if line]
        self.prices = self._prices(root)
        self.checkpoint()

    def close(self):
        runner = getattr(self, '_runner', None)
        if runner:
            try:
                client = getattr(self.model, 'root_async_client', None)
                if client:
                    runner.run(client.close())
            finally:
                runner.close()
                self._runner = None

    @staticmethod
    def _prices(root):
        # Read the project's literal price table without importing its global client.
        import ast
        source = root / 'src/llm_interface/llm_provider.py'
        for node in ast.parse(source.read_text()).body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'DEEPSEEK_PRICE_PER_1M_TOKENS' for t in node.targets
            ):
                return ast.literal_eval(node.value)
        return {}

    def checkpoint(self):
        write_json(self.output / 'budget.json', {'logical_calls': self.counts, 'deadline': self.deadline})

    def _record(self, record):
        self.records.append(record)
        with (self.output / 'usage.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')
            handle.flush()
            os.fsync(handle.fileno())
        groups = {}
        for phase in ('analysis', 'query', 'total'):
            rows = [r for r in self.records if phase == 'total' or r['phase'] == phase]
            groups[phase] = {'physical_requests': len(rows),
                'known_total_tokens': sum((r.get('usage') or {}).get('total_tokens', 0) for r in rows),
                'known_input_tokens': sum((r.get('usage') or {}).get('input_tokens', 0) for r in rows),
                'known_output_tokens': sum((r.get('usage') or {}).get('output_tokens', 0) for r in rows),
                'known_cached_tokens': sum(((r.get('usage') or {}).get('input_token_details') or {}).get('cache_read', 0) for r in rows),
                'known_reasoning_tokens': sum(((r.get('usage') or {}).get('output_token_details') or {}).get('reasoning', 0) for r in rows),
                'unknown_usage_requests': sum(r['usage'] is None for r in rows),
                'unknown_cost_requests': sum(r['cost'] is None for r in rows),
                'known_cost_by_currency': {'CNY': sum(r['cost'] or 0 for r in rows)}}
        write_json(self.output / 'usage_summary.json', groups)

    @timed('llm.logical_call', 'llm')
    def call(self, messages, tools, phase):
        maximum = self.limits.analysis_max_model_calls if phase == 'analysis' else self.limits.max_query_model_calls
        remaining(self.deadline, 1)
        if self.counts[phase] >= maximum:
            raise BudgetExceeded(phase + ' model-call limit')
        self.counts[phase] += 1
        self.checkpoint()
        logical = f'{phase}-{self.counts[phase]:03d}'
        archive = self.output / 'calls' / logical
        write_json(archive / 'messages.json', messages_to_dict(messages))
        attempts = 0
        previous_end = None

        def physical(_):
            nonlocal attempts, previous_end
            attempts += 1
            started = time.time()
            started_mono = time.monotonic()
            timeout = remaining(self.deadline, self.limits.llm_request_timeout_seconds)
            record = {'task_id': self.output.name, 'phase': phase, 'logical_call_id': logical,
                      'retry_index': attempts - 1, 'configured_model': self.model_name,
                      'request_local_id': str(uuid.uuid4()), 'started_at': started,
                      'usage': None, 'cost': None, 'currency': 'CNY', 'status': 'failed',
                      'pricing_source': 'project_DEEPSEEK_PRICE_PER_1M_TOKENS',
                      'pricing_recorded_at': started,
                      'price_snapshot': self.prices.get(self.model_name)}
            record.update(first_event_seconds=None, first_text_seconds=None,
                last_event_seconds=None, event_count=0, timeout_kind=None,
                request_timeout_seconds=timeout,
                read_timeout_seconds=self.limits.llm_read_timeout_seconds,
                retry_wait_before_seconds=0 if previous_end is None else started_mono - previous_end)
            aggregate = None
            async def consume(bound):
                nonlocal aggregate
                stream = bound.astream(messages, stream_usage=True,
                    timeout=httpx.Timeout(self.limits.llm_read_timeout_seconds,
                        connect=self.limits.llm_connect_timeout_seconds,
                        write=self.limits.llm_write_timeout_seconds,
                        pool=self.limits.llm_pool_timeout_seconds))
                deadline_scope = asyncio.timeout(timeout)
                try:
                    async with deadline_scope:
                        async for chunk in stream:
                            elapsed = time.monotonic() - started_mono
                            record['event_count'] += 1
                            if record['first_event_seconds'] is None:
                                record['first_event_seconds'] = elapsed
                            record['last_event_seconds'] = elapsed
                            aggregate = chunk if aggregate is None else aggregate + chunk
                            if isinstance(chunk.content, str) and chunk.content:
                                if record['first_text_seconds'] is None:
                                    record['first_text_seconds'] = elapsed
                                sys.stdout.write(chunk.content)
                                sys.stdout.flush()
                except TimeoutError as exc:
                    if deadline_scope.expired():
                        if self.deadline <= started + self.limits.llm_request_timeout_seconds:
                            record['timeout_kind'] = 'task_deadline'
                            raise BudgetExceeded('Task wall-clock budget exhausted during LLM request') from exc
                        record['timeout_kind'] = 'request_total'
                        raise RequestDeadlineExceeded('LLM request total deadline exceeded') from exc
                    raise
                finally:
                    await stream.aclose()
            try:
                bound = self.model.bind_tools(tools) if tools else self.model
                print(f'\n[{logical} request {attempts}]', flush=True)
                if getattr(self, '_runner', None) is None:
                    self._runner = asyncio.Runner()
                with timing_span('llm.physical_request', 'llm', phase=phase,
                                 logical_call_id=logical, retry_index=attempts - 1):
                    self._runner.run(consume(bound), context=copy_context())
                if aggregate is None:
                    raise TransientLLMError('Empty stream')
                message = message_chunk_to_message(aggregate)
                if not message.content and not message.tool_calls:
                    raise TransientLLMError('Empty response')
                record['status'] = 'success'
                write_json(archive / f'response-{attempts}.json', messages_to_dict([message]))
                return message
            except Exception as exc:
                record['error_type'] = type(exc).__name__
                causes = []
                cause = exc
                while cause is not None and type(cause).__name__ not in causes:
                    causes.append(type(cause).__name__)
                    cause = cause.__cause__
                record['error_chain'] = causes
                if record['timeout_kind'] is None:
                    for kind in ('ReadTimeout', 'ConnectTimeout', 'WriteTimeout', 'PoolTimeout'):
                        if kind in causes:
                            record['timeout_kind'] = kind
                            break
                if isinstance(exc, (RequestDeadlineExceeded, BudgetExceeded)):
                    raise
                code = getattr(exc, 'status_code', None)
                if isinstance(exc, TransientLLMError) or isinstance(exc, TimeoutError) or code == 429 or (
                    isinstance(code, int) and code >= 500
                ) or any(s in type(exc).__name__.lower() for s in ('connection', 'timeout')):
                    raise TransientLLMError(type(exc).__name__) from exc
                raise
            finally:
                if aggregate is not None:
                    record['usage'] = getattr(aggregate, 'usage_metadata', None)
                    meta = getattr(aggregate, 'response_metadata', {})
                    record['response_model'] = meta.get('model_name')
                    record['provider_request_id'] = meta.get('id') or meta.get('request_id')
                    if record['status'] != 'success':
                        write_json(archive / f'partial-{attempts}.json', messages_to_dict([aggregate]))
                usage, price = record['usage'], self.prices.get(self.model_name)
                if usage is not None and price:
                    incoming, outgoing = usage.get('input_tokens'), usage.get('output_tokens')
                    details = usage.get('input_token_details') or {}
                    cached = details.get('cache_read')
                    # Missing cache breakdown cannot support exact provider-tier costing.
                    if incoming is not None and outgoing is not None and cached is not None:
                        record['cost'] = (cached * price['input_cache_hit'] +
                            max(0, incoming - cached) * price['input_cache_miss'] +
                            outgoing * price['output']) / 1_000_000
                    record['cost_is_estimate'] = True
                record['ended_at'] = time.time()
                if record['cost'] is None:
                    record['cost_unknown_reason'] = ('usage_missing' if usage is None else
                        'price_missing' if not price else 'cache_or_token_breakdown_missing')
                record['duration_seconds'] = time.monotonic() - started_mono
                previous_end = time.monotonic()
                self._record(record)
                print(flush=True)

        return RunnableLambda(physical).with_retry(
            retry_if_exception_type=(TransientLLMError,),
            stop_after_attempt=self.limits.llm_transport_retries + 1,
            wait_exponential_jitter=True,
            exponential_jitter_params={'initial': 1, 'max': 10},
        ).invoke(None)
