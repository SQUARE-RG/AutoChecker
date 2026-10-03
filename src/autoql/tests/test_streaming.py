from pathlib import Path
import tempfile
import time
import unittest
import asyncio
import httpx

from langchain_core.messages import AIMessageChunk, HumanMessage

from autoql.llm import StreamingLLM, RequestDeadlineExceeded
from autoql.runtime import Limits, BudgetExceeded


class FakeModel:
    def __init__(self, responses):
        self.responses = iter(responses)

    def bind_tools(self, tools):
        return self

    async def astream(self, messages, **kwargs):
        for item in next(self.responses):
            if isinstance(item, Exception):
                raise item
            yield item


class StreamingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.gateway = StreamingLLM.__new__(StreamingLLM)
        self.gateway.output = Path(self.temp.name)
        self.gateway.limits = Limits(llm_transport_retries=1)
        self.gateway.deadline = time.time() + 30
        self.gateway.counts = {'analysis': 0, 'query': 0}
        self.gateway.records = []
        self.gateway.model_name = 'test'
        self.gateway.prices = {'test': {'input_cache_hit': 1, 'input_cache_miss': 2, 'output': 3}}

    def tearDown(self):
        self.gateway.close()
        self.temp.cleanup()

    def test_hard_deadline_cancels_silent_stream_without_retry(self):
        class SilentModel:
            closed = False
            async def astream(self, *args, **kwargs):
                try:
                    await asyncio.sleep(10)
                    yield AIMessageChunk(content='too late')
                finally:
                    self.closed = True
        self.gateway.model = SilentModel()
        self.gateway.limits.llm_request_timeout_seconds = 0.03
        started = time.monotonic()
        with self.assertRaises(RequestDeadlineExceeded):
            self.gateway.call([], [], 'query')
        self.assertLess(time.monotonic() - started, 1)
        self.assertTrue(self.gateway.model.closed)
        self.assertEqual(len(self.gateway.records), 1)
        self.assertEqual(self.gateway.records[0]['timeout_kind'], 'request_total')

    def test_task_deadline_and_partial_stream(self):
        class SlowModel:
            async def astream(self, *args, **kwargs):
                yield AIMessageChunk(content='partial')
                await asyncio.sleep(10)
        self.gateway.model = SlowModel()
        self.gateway.deadline = time.time() + 0.03
        with self.assertRaises(BudgetExceeded):
            self.gateway.call([], [], 'query')
        self.assertEqual(len(self.gateway.records), 1)
        row = self.gateway.records[0]
        self.assertEqual(row['timeout_kind'], 'task_deadline')
        self.assertEqual(row['event_count'], 1)
        self.assertIsNotNone(row['first_text_seconds'])

    def test_total_deadline_also_bounds_active_stream(self):
        class ActiveModel:
            async def astream(self, *args, **kwargs):
                while True:
                    yield AIMessageChunk(content='')
                    await asyncio.sleep(0.005)
        self.gateway.model = ActiveModel()
        self.gateway.limits.llm_request_timeout_seconds = 0.04
        with self.assertRaises(RequestDeadlineExceeded):
            self.gateway.call([], [], 'query')
        self.assertGreater(self.gateway.records[0]['event_count'], 1)
        self.assertEqual(len(self.gateway.records), 1)

    def test_idle_timeout_classified_and_retried(self):
        self.gateway.model = FakeModel([[httpx.ReadTimeout('idle')], [AIMessageChunk(content='ok')]])
        self.assertEqual(self.gateway.call([], [], 'query').content, 'ok')
        self.assertEqual(self.gateway.records[0]['timeout_kind'], 'ReadTimeout')
        self.assertGreater(self.gateway.records[1]['retry_wait_before_seconds'], 0)

    def test_stream_usage_counted_once(self):
        self.gateway.model = FakeModel([[AIMessageChunk(content='hi'), AIMessageChunk(content='', usage_metadata={
            'input_tokens': 10, 'output_tokens': 2, 'total_tokens': 12,
            'input_token_details': {'cache_read': 4}})]])
        self.assertEqual(self.gateway.call([HumanMessage(content='x')], [], 'query').content, 'hi')
        self.assertAlmostEqual(self.gateway.records[0]['cost'], 22 / 1_000_000)
        self.assertEqual(self.gateway.records[0]['usage']['total_tokens'], 12)

    def test_partial_retry_is_discarded_and_recorded(self):
        self.gateway.model = FakeModel([[AIMessageChunk(content='partial'), TimeoutError()],
                                       [AIMessageChunk(content='complete')]])
        self.assertEqual(self.gateway.call([], [], 'query').content, 'complete')
        self.assertEqual(len(self.gateway.records), 2)
        self.assertIsNone(self.gateway.records[0]['usage'])
        self.assertIsNone(self.gateway.records[0]['cost'])
        self.assertEqual(self.gateway.counts['query'], 1)

    def test_tool_stream_and_unknown_price(self):
        self.gateway.prices = {}
        self.gateway.model = FakeModel([[AIMessageChunk(content='', tool_call_chunks=[
            {'name': 'search_docs', 'args': '{"queries":', 'id': 'call1', 'index': 0}]),
            AIMessageChunk(content='', tool_call_chunks=[{'name': None, 'args': '["java"]}', 'id': None, 'index': 0}])]])
        result = self.gateway.call([], [], 'analysis')
        self.assertEqual(result.tool_calls[0]['args'], {'queries': ['java']})
        self.assertIsNone(self.gateway.records[0]['cost'])

    def test_budget(self):
        self.gateway.counts['query'] = 40
        with self.assertRaises(BudgetExceeded):
            self.gateway.call([], [], 'query')


if __name__ == '__main__':
    unittest.main()
