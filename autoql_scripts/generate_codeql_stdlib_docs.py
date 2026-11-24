#!/usr/bin/env python3
"""Generate version-matched CodeQL standard-library HTML documentation."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUNDLE = Path("/opt/codeql-bundle-2.23.3")
DEFAULT_OUTPUT_ROOT = REPOSITORY_ROOT / "codeql-standard-libraries"


@dataclass(frozen=True)
class LanguageConfig:
    pack_name: str
    pack_directory: str
    output_directory: str
    title: str


# output_directory deliberately matches the language component in the official
# URLs, for example /codeql-standard-libraries/java/index.html.
LANGUAGES = {
    "java": LanguageConfig(
        pack_name="codeql/java-all",
        pack_directory="java-all",
        output_directory="java",
        title="CodeQL library for Java/Kotlin",
    ),
    "cpp": LanguageConfig(
        pack_name="codeql/cpp-all",
        pack_directory="cpp-all",
        output_directory="cpp",
        title="CodeQL library for C/C++",
    ),
    "python": LanguageConfig(
        pack_name="codeql/python-all",
        pack_directory="python-all",
        output_directory="python",
        title="CodeQL library for Python",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate qldoc HTML under codeql-standard-libraries/<language>, "
            "matching the URL layout used by codeql.github.com."
        )
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        default=DEFAULT_BUNDLE,
        help=f"CodeQL bundle root (default: {DEFAULT_BUNDLE})",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Parent output directory (default: {DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        choices=tuple(LANGUAGES),
        default=list(LANGUAGES),
        help="Languages to generate (default: java cpp python)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing language directory after a successful generation",
    )
    return parser.parse_args()


def read_pack_metadata(qlpack_file: Path) -> tuple[str, str, str | None]:
    text = qlpack_file.read_text(encoding="utf-8")

    def value(pattern: str, field: str, required: bool = True) -> str | None:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1).strip().strip("'\"")
        if required:
            raise RuntimeError(f"Missing {field!r} in {qlpack_file}")
        return None

    name = value(r"^name:\s*(\S+)\s*$", "name")
    version = value(r"^version:\s*(\S+)\s*$", "version")
    cli_version = value(r"^\s+cliVersion:\s*(\S+)\s*$", "buildMetadata.cliVersion", False)
    assert name is not None and version is not None
    return name, version, cli_version


def get_cli_version(codeql: Path) -> str:
    result = subprocess.run(
        [str(codeql), "version"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    match = re.search(r"release\s+([0-9]+(?:\.[0-9]+)+)", result.stdout)
    if not match:
        raise RuntimeError(f"Could not determine CodeQL version from:\n{result.stdout}")
    return match.group(1)


def resolve_pack(bundle: Path, config: LanguageConfig, cli_version: str) -> tuple[Path, str]:
    pack_parent = bundle / "qlpacks" / "codeql" / config.pack_directory
    candidates: list[tuple[Path, str, str | None]] = []
    for qlpack_file in sorted(pack_parent.glob("*/qlpack.yml")):
        name, version, pack_cli_version = read_pack_metadata(qlpack_file)
        if name == config.pack_name:
            candidates.append((qlpack_file.parent, version, pack_cli_version))

    matching = [item for item in candidates if item[2] == cli_version]
    if len(matching) != 1:
        found = ", ".join(
            f"{path} (pack={version}, cli={pack_cli or 'unknown'})"
            for path, version, pack_cli in candidates
        ) or "none"
        raise RuntimeError(
            f"Expected exactly one {config.pack_name} pack for CLI {cli_version}; found: {found}"
        )

    pack_path, pack_version, _ = matching[0]
    return pack_path, pack_version


def existing_output_matches(output: Path, pack_name: str, pack_version: str) -> bool:
    index = output / "index.html"
    if not index.is_file():
        return False
    text = index.read_text(encoding="utf-8")
    return (
        'name="generator" content="qldoc"' in text
        and f"<code>{pack_name}</code>" in text
        and f"<code>{pack_version}</code>" in text
    )


def install_generated_directory(generated: Path, output: Path) -> None:
    if not output.exists():
        generated.replace(output)
        return

    backup = output.with_name(f".{output.name}.backup-{uuid.uuid4().hex}")
    output.replace(backup)
    try:
        generated.replace(output)
    except BaseException:
        backup.replace(output)
        raise
    shutil.rmtree(backup)


def generate_language(
    codeql: Path,
    cli_version: str,
    language: str,
    config: LanguageConfig,
    pack_path: Path,
    pack_version: str,
    output_root: Path,
    force: bool,
) -> None:
    output = output_root / config.output_directory
    relative_url = f"/codeql-standard-libraries/{config.output_directory}/index.html"

    if output.exists() and not force:
        if existing_output_matches(output, config.pack_name, pack_version):
            print(
                f"[{language}] already generated: {output} "
                f"({config.pack_name}@{pack_version}, URL {relative_url})"
            )
            return
        raise RuntimeError(
            f"Output already exists but does not match {config.pack_name}@{pack_version}: {output}. "
            "Use --force to replace it."
        )

    generated = output_root / f".{config.output_directory}.generating-{uuid.uuid4().hex}"
    title = f"{config.title} (CodeQL CLI {cli_version})"
    command = [
        str(codeql),
        "generate",
        "library-doc",
        f"--dir={pack_path}",
        f"--output={generated}",
        f"--language={language}",
        f"--title={title}",
    ]

    print(f"[{language}] generating {config.pack_name}@{pack_version}")
    print(f"[{language}] pack: {pack_path}")
    print(f"[{language}] output: {output}")
    try:
        subprocess.run(command, check=True)
        if not existing_output_matches(generated, config.pack_name, pack_version):
            raise RuntimeError(f"Generated index failed validation: {generated / 'index.html'}")
        install_generated_directory(generated, output)
    finally:
        if generated.exists():
            shutil.rmtree(generated)

    html_count = sum(1 for _ in output.rglob("*.html"))
    print(f"[{language}] generated {html_count} HTML files; URL {relative_url}")


def main() -> int:
    args = parse_args()
    bundle = args.bundle.resolve()
    output_root = args.output_root.resolve()
    codeql = bundle / "codeql"

    if not codeql.is_file():
        raise RuntimeError(f"CodeQL executable not found: {codeql}")

    cli_version = get_cli_version(codeql)
    output_root.mkdir(parents=True, exist_ok=True)
    print(f"CodeQL CLI: {cli_version} ({codeql})")
    print(f"Output root: {output_root}")

    for language in dict.fromkeys(args.languages):
        config = LANGUAGES[language]
        pack_path, pack_version = resolve_pack(bundle, config, cli_version)
        generate_language(
            codeql=codeql,
            cli_version=cli_version,
            language=language,
            config=config,
            pack_path=pack_path,
            pack_version=pack_version,
            output_root=output_root,
            force=args.force,
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
