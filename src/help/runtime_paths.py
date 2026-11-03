"""Paths for disposable AutoChecker runtime artifacts."""

from __future__ import annotations

from pathlib import Path

from config import global_config


def runtime_temp_file(subdirectory: str, filename: str) -> Path:
    """Return a file below the configured runtime temp root and create its parent."""
    directory = (
        Path(global_config["checker"]["temp_test_dir"])
        .expanduser()
        .resolve()
        / subdirectory
    )
    directory.mkdir(parents=True, exist_ok=True)
    return directory / filename
