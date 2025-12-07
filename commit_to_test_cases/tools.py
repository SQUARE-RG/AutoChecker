import datetime
import html
import io
import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path
from queue import Queue

from bs4 import BeautifulSoup
from loguru import logger
from kparser.kfunction import KernelFunction

def get_changed_lines_in_diff(diff):
    lines = []
    for line in diff.split("\n"):
        if line.startswith("@@"):
            match = re.search(r"@@ -(\d*),.* @@.*", line)
            if match:
                lines.append(match.group(1))
    return lines

def get_function_codes(commit, include_whole_file_fallback=True, max_file_size_kb=100):
    """
    Extract function codes from commit diffs using tree-sitter.

    Args:
        commit: Git commit object
        include_whole_file_fallback: If True, include whole file content when tree-sitter fails
        max_file_size_kb: Maximum file size in KB to include as whole file (default: 100KB)

    Returns:
        Set of tuples: (file_path, function_name, function_code)
    """
    codes = set()
    # 计算当前提交与其父提交之间的差异，并生成详细的补丁信息。
    # diff.a_path和 diff.b_path: 更改前后文件的路径
    diffs = commit.diff(commit.hexsha + "^", create_patch=True)

    for diff in diffs:
        if diff.a_path.endswith(".c") or diff.a_path.endswith(".h"):
            file_content_before = commit.repo.git.show(
                f"{commit.hexsha}^:{diff.a_path}"
            )
            changed_lines = get_changed_lines_in_diff(diff.diff.decode("utf-8"))

            # Try to extract functions using tree-sitter
            temp_file = Path("__temp.c")
            temp_file.write_text(file_content_before)

            try:
                functions = KernelFunction.from_file(temp_file)
                if temp_file.exists():
                    temp_file.unlink()

                # Check if we found any functions containing changed lines
                functions_found = False
                for func in functions:
                    for line in changed_lines:
                        start_line, end_line = func.get_line_numbers()
                        if start_line <= int(line) <= end_line:
                            codes.add((diff.a_path, func.name, func.code))
                            functions_found = True

                # Fallback: if tree-sitter didn't find any relevant functions, include whole file
                if not functions_found and include_whole_file_fallback:
                    file_size_kb = len(file_content_before.encode("utf-8")) / 1024

                    if file_size_kb <= max_file_size_kb:
                        logger.warning(
                            f"Tree-sitter failed to find functions for {diff.a_path}, including whole file ({file_size_kb:.1f}KB)"
                        )

                        # Create a "whole file" entry
                        file_name = Path(diff.a_path).name
                        codes.add(
                            (
                                diff.a_path,
                                f"WHOLE_FILE_{file_name}",
                                file_content_before,
                            )
                        )
                    else:
                        logger.warning(
                            f"Tree-sitter failed for {diff.a_path}, but file too large ({file_size_kb:.1f}KB > {max_file_size_kb}KB), skipping"
                        )

            except Exception as e:
                logger.error(f"Tree-sitter parsing failed for {diff.a_path}: {e}")

                # Clean up temp file if it exists
                if temp_file.exists():
                    temp_file.unlink()

                # Fallback: include whole file when tree-sitter completely fails
                if include_whole_file_fallback:
                    file_size_kb = len(file_content_before.encode("utf-8")) / 1024

                    if file_size_kb <= max_file_size_kb:
                        logger.warning(
                            f"Including whole file {diff.a_path} due to tree-sitter failure ({file_size_kb:.1f}KB)"
                        )
                        file_name = Path(diff.a_path).name
                        codes.add(
                            (
                                diff.a_path,
                                f"WHOLE_FILE_{file_name}",
                                file_content_before,
                            )
                        )
                    else:
                        logger.warning(
                            f"Tree-sitter failed for {diff.a_path}, but file too large ({file_size_kb:.1f}KB > {max_file_size_kb}KB), skipping"
                        )

    return codes


def get_function_codes_with_config(commit):
    """
    Wrapper function that uses global config for fallback behavior.
    """
    try:
        from global_config import global_config

        # Check if whole file fallback is enabled in config
        fallback_enabled = global_config.get("tree_sitter_fallback_enabled", True)
        max_file_size = global_config.get("tree_sitter_fallback_max_size_kb", 100)

        return get_function_codes(commit, fallback_enabled, max_file_size)
    except ImportError:
        # Fallback to default behavior if global_config is not available
        return get_function_codes(commit)

def truncate_large_file(content: str, max_lines: int = 500) -> str:
    """
    Truncate file content if it's too large, keeping the beginning and end.

    Args:
        content: File content to potentially truncate
        max_lines: Maximum number of lines to keep

    Returns:
        Truncated content with indication if truncation occurred
    """
    lines = content.split("\n")
    if len(lines) <= max_lines:
        return content

    # Keep first and last portions
    keep_each = max_lines // 2
    first_part = lines[:keep_each]
    last_part = lines[-keep_each:]

    truncated_content = "\n".join(first_part)
    truncated_content += (
        f"\n\n// ... [TRUNCATED: {len(lines) - max_lines} lines omitted] ...\n\n"
    )
    truncated_content += "\n".join(last_part)

    return truncated_content