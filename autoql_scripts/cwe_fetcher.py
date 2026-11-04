#!/usr/bin/env python3
"""Download MITRE CWE data and persist dataset-relevant weaknesses as JSON."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any
import xml.etree.ElementTree as ET
import zipfile

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "autoql_data" / "project_info.csv"
DEFAULT_OUTPUT = ROOT / "autoql_data" / "cwe_info.json"
CWE_XML_URL = "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_cwe_id(value: str) -> str:
    """Normalize CWE-022 and CWE-22 to the canonical value CWE-22."""
    match = re.fullmatch(r"CWE-0*(\d+)", value.strip(), flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid CWE ID: {value!r}")
    return f"CWE-{int(match.group(1))}"


def dataset_cwe_names(dataset_path: Path) -> dict[str, str]:
    with dataset_path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        result: dict[str, str] = {}
        for row in rows:
            raw_id = row.get("cwe_id", "").strip()
            if not raw_id:
                continue
            cwe_id = canonical_cwe_id(raw_id)
            name = re.sub(
                r"^CWE-0*\d+\s*:\s*", "", row.get("cwe_name", "").strip(),
                flags=re.IGNORECASE,
            )
            # Historical dataset rows can use old CWE names (for example,
            # "Information Exposure") or prefix the name with its ID. MITRE's
            # current catalog remains authoritative for present entries; the
            # first normalized dataset name is only a fallback for absent IDs.
            if name or cwe_id not in result:
                result.setdefault(cwe_id, name)
    return dict(sorted(
        result.items(), key=lambda pair: int(pair[0].split("-", 1)[1])
    ))


def dataset_cwe_ids(dataset_path: Path) -> list[str]:
    return list(dataset_cwe_names(dataset_path))


def download_cwe_xml(url: str = CWE_XML_URL, timeout: float = 300.0) -> str:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    with tempfile.TemporaryDirectory() as directory:
        archive_path = Path(directory) / "cwec_latest.xml.zip"
        archive_path.write_bytes(response.content)
        with zipfile.ZipFile(archive_path) as archive:
            members = [name for name in archive.namelist() if name.lower().endswith(".xml")]
            if not members:
                raise ValueError("MITRE CWE archive contains no XML document")
            if len(members) != 1:
                raise ValueError(f"MITRE CWE archive contains multiple XML documents: {members}")
            return archive.read(members[0]).decode("utf-8")


def element_text(element: ET.Element | None) -> str:
    return " ".join("".join(element.itertext()).split()) if element is not None else ""


def child_text(element: ET.Element, namespace: dict[str, str], name: str) -> str:
    return element_text(element.find(f"cwe:{name}", namespace))


def parse_consequences(element: ET.Element, namespace: dict[str, str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for consequence in element.findall(".//cwe:Common_Consequences/cwe:Consequence", namespace):
        scopes = [element_text(value) for value in consequence.findall("cwe:Scope", namespace)]
        impacts = [element_text(value) for value in consequence.findall("cwe:Impact", namespace)]
        record = {
            "scopes": ", ".join(value for value in scopes if value),
            "impacts": ", ".join(value for value in impacts if value),
            "note": child_text(consequence, namespace, "Note"),
        }
        if any(record.values()):
            result.append(record)
    return result


def parse_mitigations(element: ET.Element, namespace: dict[str, str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for mitigation in element.findall(".//cwe:Potential_Mitigations/cwe:Mitigation", namespace):
        phases = [element_text(value) for value in mitigation.findall("cwe:Phase", namespace)]
        record = {
            "phases": ", ".join(value for value in phases if value),
            "description": child_text(mitigation, namespace, "Description"),
        }
        if any(record.values()):
            result.append(record)
    return result


def parse_cwe_xml(xml_content: str) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    root = ET.fromstring(xml_content)
    namespace_uri = root.tag.partition("}")[0].removeprefix("{")
    if not namespace_uri:
        raise ValueError("MITRE CWE XML document has no namespace")
    namespace = {"cwe": namespace_uri}
    container = root.find("cwe:Weaknesses", namespace)
    if container is None:
        raise ValueError("MITRE CWE XML document has no Weaknesses container")

    items: dict[str, dict[str, Any]] = {}
    for weakness in container.findall("cwe:Weakness", namespace):
        raw_id = weakness.get("ID", "").strip()
        if not raw_id.isdigit():
            continue
        cwe_id = canonical_cwe_id("CWE-" + raw_id)
        items[cwe_id] = {
            "cwe_id": cwe_id,
            "entry_type": "weakness",
            "catalog_present": True,
            "name": weakness.get("Name", ""),
            "description": child_text(weakness, namespace, "Description"),
            "extended_description": child_text(weakness, namespace, "Extended_Description"),
            "abstraction": weakness.get("Abstraction", ""),
            "structure": weakness.get("Structure", ""),
            "status": weakness.get("Status", ""),
            "likelihood_of_exploit": child_text(weakness, namespace, "Likelihood_Of_Exploit"),
            "common_consequences": parse_consequences(weakness, namespace),
            "potential_mitigations": parse_mitigations(weakness, namespace),
        }

    catalog = {
        "catalog_name": root.get("Name", "CWE"),
        "catalog_version": root.get("Version", ""),
        "catalog_date": root.get("Date", ""),
    }
    return items, catalog


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


def build_json_cache(
    dataset_path: Path,
    output_path: Path,
    include_all: bool = False,
    timeout: float = 300.0,
    xml_content: str | None = None,
) -> list[str]:
    requested_names = dataset_cwe_names(dataset_path)
    requested = list(requested_names)
    content = xml_content if xml_content is not None else download_cwe_xml(timeout=timeout)
    all_items, catalog = parse_cwe_xml(content)
    missing = sorted(set(requested) - set(all_items))
    selected = (dict(all_items) if include_all else
                {cwe_id: all_items[cwe_id]
                 for cwe_id in requested if cwe_id in all_items})
    # Some historical dataset mappings, such as CWE-264, are prohibited
    # categories and are absent from the current downloadable Weaknesses
    # catalog. Preserve their exact dataset identity without pretending that
    # MITRE supplied a current weakness definition.
    for cwe_id in missing:
        selected[cwe_id] = {
            "cwe_id": cwe_id,
            "entry_type": "dataset_fallback",
            "catalog_present": False,
            "name": requested_names[cwe_id],
            "description": "",
            "extended_description": "",
            "abstraction": "",
            "structure": "",
            "status": "absent_from_current_mitre_weakness_catalog",
            "likelihood_of_exploit": "",
            "common_consequences": [],
            "potential_mitigations": [],
        }
    selected = dict(sorted(
        selected.items(), key=lambda pair: int(pair[0].split("-", 1)[1])
    ))
    value = {
        "_meta": {
            "schema_version": SCHEMA_VERSION,
            "source": "MITRE CWE",
            "source_url": CWE_XML_URL,
            "generated_at": utc_now(),
            "dataset": str(dataset_path),
            "dataset_cwe_count": len(requested),
            "item_count": len(selected),
            "catalog_missing_ids": missing,
            **catalog,
        },
        "items": selected,
    }
    write_json_atomic(output_path, value)
    print(f"Parsed CWE weaknesses: {len(all_items)}")
    print(f"Dataset CWE IDs: {len(requested)}")
    print(f"Written CWE records: {len(selected)}")
    print(f"Output: {output_path}")
    if missing:
        print("Dataset fallback CWE IDs: " + ", ".join(missing))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="project_info.csv used to select relevant CWEs")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--all", action="store_true",
                        help="write every MITRE weakness instead of dataset-relevant CWEs")
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()
    build_json_cache(
        args.dataset.resolve(), args.output.resolve(), args.all, args.timeout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
