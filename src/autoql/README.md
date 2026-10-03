# AutoQL

Single curated fix commit → Deep Agents repository exploration → evidence-backed spec →
bounded LangGraph CodeQL generation/repair → independent file/function evaluation.

Design and implementation goal:

- [Design](../../docs/autoql_patch_query_synthesis_design.md)
- [Goal](../../docs/autoql_patch_query_synthesis_goal.md)
- [Implementation and real-commit validation report](../../docs/autoql_implementation_report.md)

## Environment

Use `code_check_autoql` (Python 3.11), cloned from the original Python 3.10 `code_check`
with user approval. Deep Agents requires Python 3.11. Do not upgrade the original environment.

```bash
conda run -n code_check_autoql python -m pip install -r src/autoql/requirements.txt
PYTHONPATH=src conda run --no-capture-output -n code_check_autoql python -m autoql.run_patch \
  --commit a0ab2fa9f492b13667810b94b5feeb86268fde9e
```

Model name, endpoint and credentials use the existing project `.env` (`MODEL_NAME`,
`DEEPSEEK_BASE_URL`, `DEEPSEEK_API_KEY`). Credentials are never included in prompts.
Streaming is mandatory for AutoQL without changing shared defaults. Prices are read from
the existing project's literal price table; costs are estimates with a recorded price snapshot.
Missing usage/pricing is unknown, never free. Inspect `usage.jsonl` and `usage_summary.json`.

## Timeouts and elapsed time

New runs default to 30s connect / 300s network read idle / 60s write / 30s pool
timeouts, plus a **600s total request deadline**. The total deadline cancels the
async stream even while awaiting an event; it is not checked only upon a chunk.
The 1800s task deadline remains the outer bound. SDK retries are disabled; transient
network failures can retry twice, but request-total/task deadline expiry is not
blindly retried. A request that is canceled locally may still be billed upstream.

`--limits` accepts JSON overrides for these `llm_*_timeout_seconds` fields.
`llm_request_timeout_seconds` means total duration, not idle duration. Resuming keeps
the run's saved limits/deadline, including older 120s settings; new defaults do not
silently grant more budget to historical runs.

`timing_events.jsonl` records nested start/end events with session/span/parent IDs.
`timing_summary.json` reports stages, per-attempt graph nodes, CodeQL commands,
LLM requests, wall time, measured active runtime and resume gaps. Durations use a
monotonic clock; timestamps use wall time for log correlation. Parent spans include
their children and must not be summed with them. Interrupted or legacy sessions
without timings are marked incomplete, never assigned invented durations.

LLM usage records additionally contain first model-event/text latency, last event
time, event count, retry wait, effective total timeout, timeout category and error
type chain. Model events are **not raw network heartbeats**; HTTPX enforces network
read-idle timeouts below the model-event layer.

## Inputs and outputs

The default dataset is `autoql_data`. The commit must uniquely match a complete fix SHA.
The baseline is the dataset's buggy SHA, **not** the fix parent. Local repository and both
finalized Java databases are required under `cves`; missing assets fail closed. No automatic
database rebuild or repository checkout changes occur.

`--preflight-only` verifies revisions, extracts callable boundaries and resolves ground truth
without any LLM calls. `--output PATH` chooses a fresh run directory. `--resume --output PATH`
continues with the saved deadline and budgets; it does not grant extra retries/time.

Run artifacts include manifest, neutral source snapshots, evidence registry, `vuln_spec.json`,
per-call prompts/responses, streaming usage, retrieval cache, query versions, compile logs,
SARIF, evaluation, state checkpoints and `result.json`. A successful run writes `final.ql`.
`query_verified` means automatic criteria passed; semantic review is a separate field.

Analysis uses a file backend with source/input write rejection and no shell/delegation tool.
Only `/work/` is writable. Query has only `search_docs` and `get_doc_detail`; Python owns all
query writes and CodeQL execution. Retrieval uses deterministic lexical ranking over the
installed official Java QL source/documentation and query examples, not Python/C++ collections.
The stable cache survives repair rounds; snippet truncation is explicit.

## Tests

```bash
PYTHONPATH=src conda run --no-capture-output -n code_check_autoql \
  python -m unittest discover -s src/autoql/tests -v
```

The first release targets Java and the curated single-fix workflow. Ambiguous input, missing
evidence, unresolved fixed-function moves, exhausted budgets and infrastructure failures are
reported rather than converted to successful zero-result scans. This is not a claim that
all six template modes have been validated on real vulnerabilities.

## Native Quick Evaluation (standalone)

`autoql.quick_eval` provides a standalone Python API, command-line entry point, and optional
LangChain tools for native CodeQL Query Server quick evaluation of predicates, classes,
formulas, and expressions. It is intentionally not connected to the generation/repair graph
yet. See [quick_eval/README.md](quick_eval/README.md) for usage and test commands.
