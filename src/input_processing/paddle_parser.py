from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import requests

from .schemas import DocumentBlock


DEFAULT_PADDLEOCR_URL = "http://127.0.0.1:18080/layout-parsing"


def call_paddleocr(
    input_path: Path,
    service_url: str = DEFAULT_PADDLEOCR_URL,
    timeout_seconds: int = 7200,
    use_table_recognition: bool = True,
    use_region_detection: bool = True,
) -> dict[str, Any]:
    suffix = input_path.suffix.lower()
    file_type = 0 if suffix == ".pdf" else 1
    payload = {
        "file": base64.b64encode(input_path.read_bytes()).decode("ascii"),
        "fileType": file_type,
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useTextlineOrientation": False,
        "useSealRecognition": False,
        "useTableRecognition": use_table_recognition,
        "useFormulaRecognition": False,
        "useChartRecognition": False,
        "useRegionDetection": use_region_detection,
        "formatBlockContent": True,
        "returnMarkdownImages": False,
        "visualize": False,
    }
    response = requests.post(
        service_url,
        json=payload,
        timeout=(30, timeout_seconds),
    )
    if not response.ok:
        raise RuntimeError(
            f"PaddleOCR returned HTTP {response.status_code}: {response.text[:2000]}"
        )
    result = response.json()
    if result.get("errorCode") not in (None, 0):
        raise RuntimeError(
            f"PaddleOCR failed: {result.get('errorCode')} {result.get('errorMsg')}"
        )
    return result


def normalize_paddleocr_response(
    response: dict[str, Any], *, page_offset: int = 0
) -> tuple[list[DocumentBlock], str, int]:
    try:
        pages = response["result"]["layoutParsingResults"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Invalid PaddleOCR response: layoutParsingResults is missing") from exc

    blocks: list[DocumentBlock] = []
    markdown_pages: list[str] = []
    for local_page_number, page_result in enumerate(pages, start=1):
        page_number = page_offset + local_page_number
        markdown = page_result.get("markdown") or {}
        markdown_text = str(markdown.get("text") or "").strip()
        markdown_pages.append(f"<!-- page: {page_number} -->\n\n{markdown_text}")

        pruned = page_result.get("prunedResult") or {}
        parsing_blocks = pruned.get("parsing_res_list") or []
        layout_boxes = (pruned.get("layout_det_res") or {}).get("boxes") or []
        for fallback_order, item in enumerate(parsing_blocks, start=1):
            raw_id = item.get("block_id", fallback_order)
            block_type = str(item.get("block_label") or "text")
            bbox = _numbers_or_none(item.get("block_bbox"))
            confidence = _match_layout_confidence(block_type, bbox, layout_boxes)
            order = item.get("block_order")
            blocks.append(
                DocumentBlock(
                    block_id=f"page-{page_number}-block-{raw_id}",
                    page=page_number,
                    type=block_type,
                    text=str(item.get("block_content") or "").strip(),
                    bbox=bbox,
                    confidence=confidence,
                    order=int(order) if isinstance(order, (int, float)) else fallback_order,
                )
            )

    return blocks, "\n\n---\n\n".join(markdown_pages).rstrip() + "\n", len(pages)


def _numbers_or_none(value: Any) -> list[float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    try:
        return [float(number) for number in value]
    except (TypeError, ValueError):
        return None


def _match_layout_confidence(
    block_type: str, bbox: list[float] | None, boxes: list[dict[str, Any]]
) -> float | None:
    if bbox is None:
        return None
    candidates: list[tuple[float, float]] = []
    for box in boxes:
        if str(box.get("label")) != block_type:
            continue
        coordinate = _numbers_or_none(box.get("coordinate"))
        if coordinate is None:
            continue
        candidates.append((_iou(bbox, coordinate), float(box.get("score", 0.0))))
    if not candidates:
        return None
    overlap, score = max(candidates)
    return score if overlap > 0.3 else None


def _iou(left: list[float], right: list[float]) -> float:
    x1, y1 = max(left[0], right[0]), max(left[1], right[1])
    x2, y2 = min(left[2], right[2]), min(left[3], right[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0
