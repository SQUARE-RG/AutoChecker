import json
from pathlib import Path

from input_processing.chunker import DocumentChunk, build_chunks
from input_processing import document_parser
from input_processing.document_parser import parse_document
from input_processing.rule_extractor import normalize_chunk_result, parse_json_response
from input_processing.rule_merger import merge_rules
from input_processing.rule_pipeline import extract_rules
from input_processing.schemas import DocumentBlock, RuleCandidate, RuleExample


def _sample_paddle_response():
    return {
        "errorCode": 0,
        "result": {
            "layoutParsingResults": [
                {
                    "markdown": {"text": "## 规则 R-1\n\n不得使用 gets。"},
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "paragraph_title",
                                "block_content": "规则 R-1",
                                "block_bbox": [0, 0, 100, 20],
                                "block_id": 0,
                                "block_order": 1,
                            },
                            {
                                "block_label": "text",
                                "block_content": "不得使用 gets。",
                                "block_bbox": [0, 21, 100, 50],
                                "block_id": 1,
                                "block_order": 2,
                            },
                        ],
                        "layout_det_res": {"boxes": []},
                    },
                }
            ],
            "dataInfo": {"numPages": 1, "type": "pdf"},
        },
    }


def test_parse_existing_paddle_response(tmp_path: Path):
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"not-used-when-importing-response")
    response = tmp_path / "response.json"
    response.write_text(json.dumps(_sample_paddle_response()), encoding="utf-8")
    output = tmp_path / "parsed"

    manifest = parse_document(source, output, response_json=response)

    assert manifest["parser_backend"] == "paddleocr-import"
    assert manifest["page_count"] == 1
    assert "不得使用 gets" in (output / "document.md").read_text(encoding="utf-8")
    blocks = json.loads((output / "blocks.json").read_text(encoding="utf-8"))["blocks"]
    assert blocks[1]["block_id"] == "page-1-block-1"


def test_pdf_batches_are_resumable_and_keep_global_pages(tmp_path: Path, monkeypatch):
    from pypdf import PdfReader, PdfWriter

    source = tmp_path / "multi.pdf"
    writer = PdfWriter()
    for _ in range(3):
        writer.add_blank_page(width=100, height=100)
    with source.open("wb") as stream:
        writer.write(stream)

    calls = []

    def fake_call(path: Path, **kwargs):
        page_count = len(PdfReader(str(path)).pages)
        calls.append(page_count)
        page = _sample_paddle_response()["result"]["layoutParsingResults"][0]
        return {
            "errorCode": 0,
            "result": {
                "layoutParsingResults": [page for _ in range(page_count)],
                "dataInfo": {"numPages": page_count, "type": "pdf"},
            },
        }

    monkeypatch.setattr(document_parser, "call_paddleocr", fake_call)
    output = tmp_path / "batched"
    first = parse_document(source, output, pdf_batch_pages=2)
    second = parse_document(source, output, pdf_batch_pages=2)

    assert first["parser_backend"] == "paddleocr-http-batched"
    assert second["page_count"] == 3
    assert calls == [2, 1]
    blocks = json.loads((output / "blocks.json").read_text(encoding="utf-8"))["blocks"]
    assert {block["page"] for block in blocks} == {1, 2, 3}
    assert any(block["block_id"].startswith("page-3-") for block in blocks)


def test_chunker_overlaps_pages():
    blocks = [
        DocumentBlock(f"page-{page}-block-1", page, "text", "x " * 180, order=1)
        for page in range(1, 5)
    ]
    chunks = build_chunks(blocks, max_tokens=500, overlap_pages=1)
    assert len(chunks) >= 2
    assert chunks[0].pages[-1] == chunks[1].pages[0]


def test_parse_json_fence():
    assert parse_json_response('```json\n{"rules": []}\n```') == {"rules": []}


def test_advisory_rule_type_and_duplicate_examples_are_normalized():
    chunk = DocumentChunk("chunk-0001", [1], ["page-1-block-1"], "建议使用安全接口。", 10)
    result = normalize_chunk_result(
        {
            "rules": [
                {
                    "rule_id": "A-1",
                    "main_title": "prefer-safe-api",
                    "description": "建议使用安全接口。",
                    "rule_type": "建议性",
                    "examples": [
                        {"type": "compliant", "code": "safe_call();"},
                        {"type": "compliant", "code": "safe_call( );"},
                    ],
                }
            ]
        },
        chunk,
    )
    assert result.rules[0].rule_type == "advisory"
    assert len(result.rules[0].examples) == 1


def test_same_numbered_rule_keeps_all_distinct_clauses():
    common = {
        "rule_id": "R-1-1-12",
        "rule_type": "required",
        "source_chunks": ["chunk-0001"],
    }
    rules = merge_rules(
        [
            RuleCandidate(
                main_title="bitfield-same-type-length",
                description="位定义的变量必须使用长度相同的基础类型。",
                examples=[RuleExample("violation", "struct A { char a:2; short b:2; };")],
                **common,
            ),
            RuleCandidate(
                main_title="bitfield-no-cross-type-boundary",
                description="位定义禁止跨越基础类型的长度边界。",
                examples=[RuleExample("compliant", "struct A { short a:2; short b:2; };")],
                **common,
            ),
        ]
    )
    assert len(rules) == 1
    assert "长度相同" in rules[0].description
    assert "禁止跨越" in rules[0].description
    assert rules[0].main_title == (
        "bitfield-same-type-length-and-no-cross-type-boundary"
    )
    assert len(rules[0].examples) == 2


def test_rule_pipeline_with_fake_llm(tmp_path: Path):
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"sample")
    response = tmp_path / "response.json"
    response.write_text(json.dumps(_sample_paddle_response()), encoding="utf-8")
    parsed = tmp_path / "parsed"
    parse_document(source, parsed, response_json=response)

    calls = 0

    def fake_invoke(prompt: str, system: str) -> str:
        nonlocal calls
        calls += 1
        return json.dumps(
            {
                "rules": [
                    {
                        "rule_id": "R-1",
                        "main_title": "do-not-use-gets",
                        "description": "C/C++ 程序不得使用 gets 函数。",
                        "rule_type": "required",
                        "examples": [
                            {
                                "type": "violation",
                                "code": "int main(void) {\n    gets(buf);\n}",
                            },
                            {
                                "type": "compliant",
                                "code": "int main(void) {\n    fgets(buf, sizeof(buf), stdin);\n}",
                            },
                        ],
                    }
                ]
            },
            ensure_ascii=False,
        )

    summary = extract_rules(
        parsed,
        category="sample",
        max_chunk_tokens=1000,
        invoke=fake_invoke,
    )
    assert calls == 1
    assert summary["rule_count"] == 1
    assert summary["non_empty_chunk_count"] == 1
    output = json.loads((parsed / "autochecker_rules.json").read_text(encoding="utf-8"))
    rule = output["data"]["sample"][0]
    assert set(rule) == {
        "rule_id",
        "main_title",
        "description",
        "rule_type",
        "source_chunks",
        "examples",
        "rule_test_path",
    }
    assert rule["rule_test_path"] == ""
    assert rule["source_chunks"] == ["chunk-0001"]
    assert rule["rule_type"] == "required"
    assert rule["examples"][0]["type"] == "violation"
    assert "\n" in rule["examples"][0]["code"]

    # Completed chunk checkpoints make the second invocation free and resumable.
    extract_rules(
        parsed,
        category="sample",
        max_chunk_tokens=1000,
        invoke=fake_invoke,
    )
    assert calls == 1


def test_non_normative_chunk_is_recorded_without_rules(tmp_path: Path):
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"sample")
    response = tmp_path / "response.json"
    response.write_text(json.dumps(_sample_paddle_response()), encoding="utf-8")
    parsed = tmp_path / "parsed"
    parse_document(source, parsed, response_json=response)

    def fake_invoke(prompt: str, system: str) -> str:
        return '{"rules": []}'

    summary = extract_rules(
        parsed,
        category="sample",
        max_chunk_tokens=1000,
        invoke=fake_invoke,
    )
    assert summary["rule_count"] == 0
    assert summary["non_empty_chunk_count"] == 0
    output = json.loads((parsed / "autochecker_rules.json").read_text(encoding="utf-8"))
    assert output == {"data": {"sample": []}}
