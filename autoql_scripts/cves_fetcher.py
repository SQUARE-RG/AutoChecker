#!/usr/bin/env python3
"""Fetch dataset CVE descriptions from NVD and persist a versioned JSON cache."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
import time
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "autoql_data" / "project_info.csv"
DEFAULT_OUTPUT = ROOT / "autoql_data" / "cve_info.json"
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def dataset_cve_ids(dataset_path: Path) -> list[str]:
    """Return the unique CVE IDs declared by project_info.csv."""
    with dataset_path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        ids = {row.get("cve_id", "").strip().upper() for row in rows}
    ids.discard("")
    invalid = sorted(
        value for value in ids if not re.fullmatch(r"CVE-\d{4}-\d{4,}", value)
    )
    if invalid:
        raise ValueError(f"Invalid CVE IDs in {dataset_path}: {invalid[:5]}")
    return sorted(ids)


def fetch_cve_from_nvd(
    cve_id: str,
    api_key: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any] | None:
    headers = {"apiKey": api_key} if api_key else {}
    response = requests.get(
        NVD_API_URL,
        params={"cveId": cve_id},
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    vulnerabilities = response.json().get("vulnerabilities", [])
    return vulnerabilities[0].get("cve") if vulnerabilities else None


def english_description(cve_data: dict[str, Any]) -> str:
    for entry in cve_data.get("descriptions", []):
        if entry.get("lang") == "en":
            return str(entry.get("value", "")).strip()
    return ""


def nvd_cwe_ids(cve_data: dict[str, Any]) -> list[str]:
    result: set[str] = set()
    for weakness in cve_data.get("weaknesses", []):
        for entry in weakness.get("description", []):
            value = str(entry.get("value", "")).strip().upper()
            if entry.get("lang") == "en" and value.startswith("CWE-"):
                result.add(value)
    return sorted(result)


def create_cve_record(cve_id: str, cve_data: dict[str, Any]) -> dict[str, Any]:
    description = english_description(cve_data)
    if not description:
        raise ValueError(f"NVD returned no English description for {cve_id}")
    return {
        "cve_id": cve_id,
        "description": description,
        "published_date": str(cve_data.get("published", "")),
        "modified_date": str(cve_data.get("lastModified", "")),
        "nvd_cwe_ids": nvd_cwe_ids(cve_data),
        "nist_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
    }


def empty_cache() -> dict[str, Any]:
    return {
        "_meta": {
            "schema_version": SCHEMA_VERSION,
            "source": "NVD CVE API 2.0",
            "source_url": NVD_API_URL,
            "generated_at": "",
            "item_count": 0,
        },
        "items": {},
    }


def load_cache(output_path: Path) -> dict[str, Any]:
    if not output_path.exists():
        return empty_cache()
    value = json.loads(output_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("items"), dict):
        raise ValueError(
            f"{output_path} is not a schema-v{SCHEMA_VERSION} CVE cache; "
            "move it aside or choose a different --output"
        )
    version = value.get("_meta", {}).get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported CVE cache schema version: {version!r}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=path.name + ".", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def fetch_to_json(
    dataset_path: Path,
    output_path: Path,
    api_key: str | None = None,
    rate_limit_delay: float = 0.6,
    test_limit: int | None = None,
    force: bool = False,
    timeout: float = 30.0,
    selected_cve: str | None = None,
) -> list[str]:
    cve_ids = dataset_cve_ids(dataset_path)
    if selected_cve is not None:
        selected_cve = selected_cve.upper()
        if selected_cve not in cve_ids:
            raise ValueError(f'{selected_cve} is not present in {dataset_path}')
        cve_ids = [selected_cve]
    if test_limit is not None:
        cve_ids = cve_ids[:test_limit]

    cache = load_cache(output_path)
    items: dict[str, Any] = cache["items"]
    delay = rate_limit_delay if api_key else max(rate_limit_delay, 12.5)
    failures: list[str] = []
    fetched = 0

    print(f"Dataset CVEs: {len(cve_ids)}")
    print(f"Existing cached CVEs: {len(items)}")
    print(f"Output: {output_path}")
    for index, cve_id in enumerate(cve_ids):
        if not force and cve_id in items:
            print(f"[{index + 1}/{len(cve_ids)}] {cve_id}: cached")
            continue
        try:
            cve_data = fetch_cve_from_nvd(cve_id, api_key, timeout)
            if cve_data is None:
                raise ValueError("NVD returned no vulnerability")
            items[cve_id] = create_cve_record(cve_id, cve_data)
            fetched += 1
            print(f"[{index + 1}/{len(cve_ids)}] {cve_id}: fetched")
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            failures.append(cve_id)
            print(f"[{index + 1}/{len(cve_ids)}] {cve_id}: FAILED: {exc}")

        # Persist after every attempted fetch so interrupted runs can resume.
        cache["items"] = dict(sorted(items.items()))
        cache["_meta"].update(generated_at=utc_now(), item_count=len(items))
        write_json_atomic(output_path, cache)
        if index < len(cve_ids) - 1:
            time.sleep(delay)

    cache["items"] = dict(sorted(items.items()))
    cache["_meta"].update(generated_at=utc_now(), item_count=len(items))
    write_json_atomic(output_path, cache)
    print(f"Fetched this run: {fetched}; cached total: {len(items)}; failures: {len(failures)}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="project_info.csv used to select CVEs")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--api-key", default=os.environ.get("NVD_API_KEY"))
    parser.add_argument("--delay", type=float, default=0.6,
                        help="seconds between requests; minimum 12.5 without an API key")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--test-limit", type=int,
                        help="only process the first N dataset CVEs")
    parser.add_argument("--cve", help="fetch one exact dataset CVE")
    parser.add_argument("--force", action="store_true",
                        help="refresh records already present in the output")
    args = parser.parse_args()
    failures = fetch_to_json(
        args.dataset.resolve(), args.output.resolve(), args.api_key,
        args.delay, args.test_limit, args.force, args.timeout, args.cve,
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
