#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


TEST_PATH_HINTS = ("/test/", "/src/test/")
DOC_PATH_HINTS = ("/docs/", "/documentation/", "/doc/")
RESOURCE_PATH_HINTS = ("/src/main/resources/", "/resources/")
BUILD_FILENAMES = {
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "gradle.properties",
}
DOC_EXTS = {".md", ".adoc", ".rst", ".txt"}
RESOURCE_EXTS = {".jelly", ".properties", ".xml", ".yml", ".yaml", ".json"}
CODE_EXTS = {".java", ".kt", ".scala", ".groovy", ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".py", ".js", ".ts"}

IMPORT_RE = re.compile(r"^\s*(import|package)\b")
COMMENT_RE = re.compile(r"^\s*(//|/\*|\*|\*/|#)")
DIFF_HEADER_RE = re.compile(r"^@@ .* @@")


@dataclass
class DiffHunk:
    file_path: str
    header: str
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)
    context_lines: List[str] = field(default_factory=list)


@dataclass
class FilePatch:
    old_path: str
    new_path: str
    file_path: str
    file_ext: str
    is_binary: bool = False
    is_test_file: bool = False
    hunks: List[DiffHunk] = field(default_factory=list)
    num_added: int = 0
    num_removed: int = 0


def should_skip_preprocessing(
    total_lines: int,
    changed_lines: int,
    hunk_count: int,
    file_count: int,
) -> bool:
    return (
        total_lines <= 150
        and changed_lines <= 50
        and hunk_count <= 8
        and file_count <= 4
    )


def _clean_line(line: str) -> str:
    return line.rstrip("\n")


def _is_test_path(path: str) -> bool:
    lowered = path.lower()
    return any(hint in lowered for hint in TEST_PATH_HINTS) or Path(path).stem.lower().endswith("test")


def _is_doc_file(path: str, ext: str) -> bool:
    lowered = path.lower()
    return ext in DOC_EXTS or any(hint in lowered for hint in DOC_PATH_HINTS)


def _is_resource_file(path: str, ext: str) -> bool:
    lowered = path.lower()
    return ext in RESOURCE_EXTS or any(hint in lowered for hint in RESOURCE_PATH_HINTS)


def _is_build_file(path: str) -> bool:
    return Path(path).name in BUILD_FILENAMES


def _is_code_file(path: str, ext: str) -> bool:
    lowered = path.lower()
    if ext not in CODE_EXTS:
        return False
    if _is_test_path(lowered):
        return False
    return True


def parse_diff(diff_text: str) -> List[FilePatch]:
    files: List[FilePatch] = []
    current_file: Optional[FilePatch] = None
    current_hunk: Optional[DiffHunk] = None

    for raw_line in diff_text.splitlines():
        line = _clean_line(raw_line)
        if line.startswith("diff --git "):
            parts = line.split()
            old_path = parts[2][2:] if len(parts) > 2 and parts[2].startswith("a/") else ""
            new_path = parts[3][2:] if len(parts) > 3 and parts[3].startswith("b/") else old_path
            file_path = new_path or old_path
            current_file = FilePatch(
                old_path=old_path,
                new_path=new_path,
                file_path=file_path,
                file_ext=Path(file_path).suffix.lower(),
                is_test_file=_is_test_path(file_path),
            )
            files.append(current_file)
            current_hunk = None
            continue

        if current_file is None:
            continue

        if line.startswith("Binary files "):
            current_file.is_binary = True
            continue

        if DIFF_HEADER_RE.match(line):
            current_hunk = DiffHunk(file_path=current_file.file_path, header=line)
            current_file.hunks.append(current_hunk)
            continue

        if current_hunk is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            current_hunk.added_lines.append(line[1:])
            current_file.num_added += 1
        elif line.startswith("-") and not line.startswith("---"):
            current_hunk.removed_lines.append(line[1:])
            current_file.num_removed += 1
        else:
            current_hunk.context_lines.append(line[1:] if line.startswith(" ") else line)

    return files


def _meaningful_changed_lines(hunk: DiffHunk) -> List[str]:
    lines = []
    for line in hunk.added_lines + hunk.removed_lines:
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    return lines


def _infer_change_kind(hunk: DiffHunk) -> str:
    lines = _meaningful_changed_lines(hunk)
    if lines and all(IMPORT_RE.match(line) for line in lines):
        return "import_only"
    if lines and all(COMMENT_RE.match(line) for line in lines):
        return "comment_only"

    normalized = [re.sub(r"\s+", "", line) for line in hunk.added_lines + hunk.removed_lines if line.strip()]
    if normalized and len(set(normalized)) <= 1 and len(normalized) > 1:
        return "format_only"

    if hunk.added_lines and hunk.removed_lines:
        return "mixed_change"
    if hunk.added_lines:
        return "add_only"
    if hunk.removed_lines:
        return "remove_only"
    return "context_only"


def _summarize_lines(lines: List[str], max_lines: int = 3) -> str:
    summary_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        summary_lines.append(stripped)
        if len(summary_lines) >= max_lines:
            break
    return " ".join(summary_lines) if summary_lines else ""


def _count_non_import_hunks(file_patch: FilePatch) -> int:
    count = 0
    for hunk in file_patch.hunks:
        if _infer_change_kind(hunk) != "import_only":
            count += 1
    return count


def _count_non_import_changed_lines(file_patch: FilePatch) -> int:
    changed = 0
    for hunk in file_patch.hunks:
        if _infer_change_kind(hunk) != "import_only":
            changed += len(hunk.added_lines) + len(hunk.removed_lines)
    return changed


def _looks_behavioral(text: str) -> bool:
    keywords = (
        "if (", "throw ", "return ", "new ", "set", "check", "validate", "normalize",
        "RequirePOST", "startsWith", "parse(", "execute(", "create", "build(", "with",
    )
    return any(keyword in text for keyword in keywords)


def _is_main_code_file(file_patch: FilePatch) -> bool:
    if not _is_code_file(file_patch.file_path, file_patch.file_ext):
        return False

    path_lower = file_patch.file_path.lower()
    non_import_hunks = _count_non_import_hunks(file_patch)
    non_import_changed_lines = _count_non_import_changed_lines(file_patch)
    text = "\n".join(
        line for h in file_patch.hunks for line in (h.added_lines + h.removed_lines)
    )

    path_hints = ("impl", "service", "controller", "action", "realm", "manager", "handler", "core", "security")
    if any(hint in path_lower for hint in path_hints):
        return True
    if non_import_hunks >= 2:
        return True
    if non_import_changed_lines >= 8:
        return True
    if _looks_behavioral(text):
        return True
    return False


def _file_summary(file_patch: FilePatch) -> str:
    parts = ["production code file"]
    parts.append(f"{len(file_patch.hunks)} hunks")
    parts.append(f"+{file_patch.num_added}/-{file_patch.num_removed}")
    if file_patch.file_ext:
        parts.append(f"extension {file_patch.file_ext}")
    return ", ".join(parts)


def _build_hunk_summary(file_patch: FilePatch, hunk: DiffHunk) -> Dict[str, object]:
    return {
        "file": file_patch.file_path,
        "header": hunk.header,
        "change_kind": _infer_change_kind(hunk),
        "added_summary": _summarize_lines(hunk.added_lines),
        "removed_summary": _summarize_lines(hunk.removed_lines),
        "added_lines_count": len(hunk.added_lines),
        "removed_lines_count": len(hunk.removed_lines),
    }


def analyze_diff(diff_text: str) -> Dict[str, object]:
    file_patches = parse_diff(diff_text)
    total_lines = len(diff_text.splitlines())
    total_files = len(file_patches)
    total_hunks = sum(len(file.hunks) for file in file_patches)
    changed_lines = sum(file.num_added + file.num_removed for file in file_patches)

    if should_skip_preprocessing(
        total_lines=total_lines,
        changed_lines=changed_lines,
        hunk_count=total_hunks,
        file_count=total_files,
    ):
        raw_files = []
        raw_hunks = []
        for file_patch in file_patches:
            raw_files.append(
                {
                    "path": file_patch.file_path,
                    "num_added": file_patch.num_added,
                    "num_removed": file_patch.num_removed,
                    "hunk_count": len(file_patch.hunks),
                    "is_test_file": file_patch.is_test_file,
                }
            )
            for hunk in file_patch.hunks:
                raw_hunks.append(
                    {
                        "file": file_patch.file_path,
                        "header": hunk.header,
                        "added_lines": hunk.added_lines,
                        "removed_lines": hunk.removed_lines,
                    }
                )

        return {
            "mode": "raw_diff",
            "reason": "diff_small_enough",
            "files": raw_files,
            "hunks": raw_hunks,
            "filtered_out": {
                "docs": 0,
                "tests": sum(1 for f in file_patches if f.is_test_file),
                "resources": 0,
                "build_files": 0,
                "non_code_files": 0,
                "binary_files": sum(1 for f in file_patches if f.is_binary),
            },
            "total_files": total_files,
            "total_hunks": total_hunks,
            "total_lines": total_lines,
            "changed_lines": changed_lines,
            "threshold": {
                "total_lines_max": 150,
                "changed_lines_max": 50,
                "hunk_count_max": 8,
                "file_count_max": 4,
            },
        }

    main_code_files = []
    secondary_code_files = []
    filtered_out = {
        "docs": 0,
        "tests": 0,
        "resources": 0,
        "build_files": 0,
        "non_code_files": 0,
        "binary_files": 0,
    }

    for file_patch in file_patches:
        path = file_patch.file_path
        ext = file_patch.file_ext

        if file_patch.is_binary:
            filtered_out["binary_files"] += 1
            continue
        if file_patch.is_test_file:
            filtered_out["tests"] += 1
            continue
        if _is_doc_file(path, ext):
            filtered_out["docs"] += 1
            continue
        if _is_resource_file(path, ext):
            filtered_out["resources"] += 1
            continue
        if _is_build_file(path):
            filtered_out["build_files"] += 1
            continue
        if not _is_code_file(path, ext):
            filtered_out["non_code_files"] += 1
            continue

        file_summary = {
            "path": file_patch.file_path,
            "file_ext": file_patch.file_ext,
            "num_added": file_patch.num_added,
            "num_removed": file_patch.num_removed,
            "hunk_count": len(file_patch.hunks),
            "summary": _file_summary(file_patch),
            "hunks": [_build_hunk_summary(file_patch, hunk) for hunk in file_patch.hunks],
        }

        if _is_main_code_file(file_patch):
            main_code_files.append(file_summary)
        else:
            secondary_code_files.append(file_summary)

    return {
        "mode": "focused_diff",
        "reason": "diff_large_enough_for_preprocessing",
        "main_code_files": main_code_files,
        "secondary_code_files": secondary_code_files,
        "filtered_out": filtered_out,
        "total_files": total_files,
        "total_hunks": total_hunks,
        "total_lines": total_lines,
        "changed_lines": changed_lines,
        "threshold": {
            "total_lines_max": 150,
            "changed_lines_max": 50,
            "hunk_count_max": 8,
            "file_count_max": 4,
        },
    }


def render_markdown(result: Dict[str, object], diff_file: str) -> str:
    lines = [
        "# Diff Focus Summary",
        "",
        f"- Diff file: `{diff_file}`",
        f"- Mode: `{result.get('mode', 'unknown')}`",
        f"- Reason: `{result.get('reason', 'unknown')}`",
        f"- Total lines: {result.get('total_lines', 'n/a')}",
        f"- Changed lines: {result.get('changed_lines', 'n/a')}",
        f"- Total files: {result['total_files']}",
        f"- Total hunks: {result['total_hunks']}",
        "",
    ]

    if result.get("mode") == "raw_diff":
        lines.append("## Files")
        for file_info in result.get("files", []):
            lines.append(
                f"- `{file_info['path']}` | hunks={file_info['hunk_count']} | "
                f"+{file_info['num_added']} / -{file_info['num_removed']}"
            )
        lines.extend(["", "## Hunks"])
        for hunk in result.get("hunks", []):
            lines.extend(
                [
                    f"### `{hunk['file']}`",
                    f"- Header: `{hunk['header']}`",
                    f"- Added lines: {len(hunk.get('added_lines', []))}",
                    f"- Removed lines: {len(hunk.get('removed_lines', []))}",
                    "",
                ]
            )
    else:
        lines.append("## Main Code Files")
        main_files = result.get("main_code_files", [])
        if not main_files:
            lines.append("- None")
        else:
            for file_info in main_files:
                lines.extend(
                    [
                        f"### `{file_info['path']}`",
                        f"- Summary: {file_info['summary']}",
                        f"- Hunks: {file_info['hunk_count']}",
                        f"- Changed lines: +{file_info['num_added']} / -{file_info['num_removed']}",
                        "",
                    ]
                )

        lines.extend(["", "## Secondary Code Files"])
        secondary_files = result.get("secondary_code_files", [])
        if not secondary_files:
            lines.append("- None")
        else:
            for file_info in secondary_files:
                lines.extend(
                    [
                        f"### `{file_info['path']}`",
                        f"- Summary: {file_info['summary']}",
                        f"- Hunks: {file_info['hunk_count']}",
                        f"- Changed lines: +{file_info['num_added']} / -{file_info['num_removed']}",
                        "",
                    ]
                )

        lines.extend(["", "## Hunks"])
        for file_info in main_files + secondary_files:
            hidden_import_hunks = 0
            for hunk in file_info.get("hunks", []):
                if hunk["change_kind"] == "import_only":
                    hidden_import_hunks += 1
                    continue
                lines.extend(
                    [
                        f"### `{hunk['file']}`",
                        f"- Header: `{hunk['header']}`",
                        f"- Change kind: `{hunk['change_kind']}`",
                        f"- Removed summary: {hunk['removed_summary'] or 'n/a'}",
                        f"- Added summary: {hunk['added_summary'] or 'n/a'}",
                        f"- Changed lines: +{hunk['added_lines_count']} / -{hunk['removed_lines_count']}",
                        "",
                    ]
                )
            if hidden_import_hunks:
                lines.extend(
                    [
                        f"### `{file_info['path']}`",
                        f"- Hidden import-only hunks: {hidden_import_hunks}",
                        "",
                    ]
                )

    filtered = result.get("filtered_out", {})
    lines.extend(
        [
            "## Filtered Out",
            f"- Docs: {filtered.get('docs', 0)}",
            f"- Tests: {filtered.get('tests', 0)}",
            f"- Resources: {filtered.get('resources', 0)}",
            f"- Build files: {filtered.get('build_files', 0)}",
            f"- Non-code files: {filtered.get('non_code_files', 0)}",
            f"- Binary files: {filtered.get('binary_files', 0)}",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def process_diff_file(
    diff_path: str,
    out_dir: Optional[str] = None,
) -> Dict[str, str]:
    diff_file = Path(diff_path)
    diff_text = diff_file.read_text(encoding="utf-8")
    result = analyze_diff(diff_text)
    result["diff_file"] = str(diff_file)

    out_base = Path(out_dir) if out_dir else diff_file.parent
    out_base.mkdir(parents=True, exist_ok=True)
    stem = diff_file.stem
    json_path = out_base / f"{stem}.diff_focus.json"
    md_path = out_base / f"{stem}.diff_focus.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(result, str(diff_file)), encoding="utf-8")

    return {
        "json": str(json_path),
        "markdown": str(md_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Structured diff summarizer")
    parser.add_argument("--diff", required=True, help="Path to unified diff file")
    parser.add_argument("--out-dir", help="Output directory for diff focus artifacts")
    args = parser.parse_args()

    outputs = process_diff_file(
        diff_path=args.diff,
        out_dir=args.out_dir,
    )
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
