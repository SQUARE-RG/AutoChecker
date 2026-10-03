from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


PADDLEOCR_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".html", ".htm"}
WORD_SUFFIXES = {".doc", ".docx"}


def prepare_input(input_path: Path, converted_dir: Path) -> tuple[Path, str]:
    suffix = input_path.suffix.lower()
    if suffix in PADDLEOCR_SUFFIXES:
        return input_path, "paddleocr"
    if suffix in TEXT_SUFFIXES:
        return input_path, "text"
    if suffix in WORD_SUFFIXES:
        return _convert_word_to_pdf(input_path, converted_dir), "paddleocr"
    raise ValueError(f"Unsupported input format: {suffix or '<no extension>'}")


def _convert_word_to_pdf(input_path: Path, converted_dir: Path) -> Path:
    executable = shutil.which("libreoffice") or shutil.which("soffice")
    if executable is None:
        raise RuntimeError("DOC/DOCX conversion requires LibreOffice (libreoffice or soffice)")
    converted_dir.mkdir(parents=True, exist_ok=True)
    command = [
        executable,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(converted_dir),
        str(input_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    output_path = converted_dir / f"{input_path.stem}.pdf"
    if result.returncode != 0 or not output_path.exists():
        raise RuntimeError(
            "LibreOffice conversion failed: "
            + (result.stderr.strip() or result.stdout.strip() or "unknown error")
        )
    return output_path
