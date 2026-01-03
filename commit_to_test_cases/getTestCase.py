"""Generate clang-tidy ready code slices from a kernel commit."""

# python commit_to_test_cases/getTestCase.py --commit_file=commits/commits-debug.txt
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from git import GitCommandError, exc
from loguru import logger

from target.factory import TargetFactory
from target.linux import Linux

SUPPORTED_EXTENSIONS = {
    ".c",
    ".h",
    ".cc",
    ".hh",
    ".hpp",
    ".cpp",
    ".cxx",
}

DEFAULT_COMMIT_FILE = (
    Path(__file__).resolve().parents[1] / "commits" / "commits-debug.txt"
)
TARGET_REPO_PATH = Path("/root/code_check/linux")
target = Linux(repo_path=TARGET_REPO_PATH)


def is_supported_source(path: Optional[str]) -> bool:
    if not path:
        return False
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def write_text_file(root: Path, relative_path: str, content: str) -> Path:
    # target = root / relative_path
    # print("Writing file:", root, relative_path)
    # relative_path =  drivers/spi/spi-pci1xxxx.c  截取获得spi-pci1xxxx.c
    target = root / Path(relative_path).name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return target

# 获取指定修订版中文件的内容快照
def get_file_snapshot(repo, revision: str, file_path: str) -> Optional[str]:
    try:
        return repo.git.show(f"{revision}:{file_path}")
    except GitCommandError as error:
        stderr = getattr(error, "stderr", "") or str(error)
        logger.warning(
            "Failed to read {}@{}: {}",
            file_path,
            revision[:12],
            stderr.strip(),
        )
    return None


def classify_diff(diff) -> str:
    if diff.new_file:
        return "added"
    if diff.deleted_file:
        return "deleted"
    if diff.renamed:
        return "renamed"
    return "modified"


def collect_code_slices(commit, output_dir: Path) -> List[Dict[str, Optional[str]]]:
    if not commit.parents:
        raise ValueError("Cannot analyse root commits without a parent snapshot")

    parent = commit.parents[0]
    repo = commit.repo

    before_dir = output_dir / "before"
    after_dir = output_dir / "after"
    before_dir.mkdir(parents=True, exist_ok=True)
    after_dir.mkdir(parents=True, exist_ok=True)

    entries: List[Dict[str, Optional[str]]] = []

    diffs = commit.diff(parent, create_patch=True)
    for diff in diffs:
        candidate_paths = tuple(
            path for path in (diff.a_path, diff.b_path) if path is not None
        )
        if not any(is_supported_source(path) for path in candidate_paths):
            continue

        entry: Dict[str, Optional[str]] = {
            "status": classify_diff(diff),
            "old_path": diff.a_path,
            "new_path": diff.b_path,
            "before_file": None,
            "after_file": None,
        }

        if diff.a_path and not diff.new_file and is_supported_source(diff.a_path):
            before_content = get_file_snapshot(repo, parent.hexsha, diff.a_path)
            if before_content is not None:
                before_file = write_text_file(before_dir, diff.a_path, before_content)
                entry["before_file"] = str(before_file.relative_to(output_dir))

        if diff.b_path and not diff.deleted_file and is_supported_source(diff.b_path):
            after_content = get_file_snapshot(repo, commit.hexsha, diff.b_path)
            if after_content is not None:
                after_file = write_text_file(after_dir, diff.b_path, after_content)
                entry["after_file"] = str(after_file.relative_to(output_dir))

        if entry["before_file"] or entry["after_file"]:
            entries.append(entry)

    return entries


def dump_commit_artifacts(commit, output_dir: Path) -> None:
    patch_markdown = target.get_patch(commit.hexsha)
    (output_dir / "patch.md").write_text(patch_markdown)

    if commit.parents:
        parent_sha = commit.parents[0].hexsha
        diff_text = commit.repo.git.diff(parent_sha, commit.hexsha)
        (output_dir / "changes.patch").write_text(diff_text)


def build_metadata(
    commit,
    slice_entries: List[Dict[str, Optional[str]]],
    bug_type: Optional[str],
) -> Dict[str, object]:
    parent_sha = commit.parents[0].hexsha if commit.parents else None
    return {
        "commit": commit.hexsha,
        "parent": parent_sha,
        "summary": commit.summary,
        "message": commit.message.strip(),
        "bug_type": bug_type,
        "files": slice_entries,
    }





def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract full pre/post-change source files for clang-tidy analysis of a commit"
        )
    )
    parser.add_argument(
        "--commit_file",
        default=None,
        help="CSV file containing commit sha and bug type (defaults to ../commits/commits-debug.txt)",
    )
    # parser.add_argument(
    #     "--config_file",
    #     default="config-generate.yaml",
    #     help="Path to the configuration file (default: config-generate.yaml)",
    # )
    parser.add_argument(
        "--output_dir",
        default=None,
        help="Directory to store extracted artifacts (defaults to result_dir/testcases)",
    )
    return parser.parse_args()


def load_commits(commit_file: Path) -> Sequence[Tuple[str, Optional[str]]]:
    if not commit_file.exists():
        raise FileNotFoundError(f"Commit file '{commit_file}' does not exist")

    commits: List[Tuple[str, Optional[str]]] = []
    for line in commit_file.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = [part.strip() for part in stripped.split(",", maxsplit=1)]
        if len(parts[0]) == 0:
            continue

        commit_sha = parts[0]
        bug_type = parts[1] if len(parts) > 1 else None
        commits.append((commit_sha, bug_type))

    return commits


def process_commit(
    repo,
    commit_sha: str,
    bug_type: Optional[str],
    output_root: Path,
) -> None:
    try:
        commit = repo.commit(commit_sha)
    except exc.BadName as error:
        logger.error("Commit '{}' not found: {}", commit_sha, error)
        return

    if len(commit.parents) != 1:
        logger.warning(
            "Skipping commit {} (expected single parent, found {})",
            commit.hexsha,
            len(commit.parents),
        )
        return

    bug_suffix = f"-{bug_type}" if bug_type else ""
    commit_dir = output_root / f"{commit.hexsha}{bug_suffix}"
    commit_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Collecting artifacts for commit {} {}",
        commit.hexsha,
        f"[{bug_type}]" if bug_type else "",
    )

    dump_commit_artifacts(commit, commit_dir)
    slice_entries = collect_code_slices(commit, commit_dir)

    metadata = build_metadata(commit, slice_entries, bug_type)
    (commit_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    logger.info(
        "Generated {} source slices under {}",
        len(slice_entries),
        commit_dir.resolve(),
    )


def main():
    args = parse_args()
    # target_linux = Linux(repo_path=TARGET_REPO_PATH)
    
    
    repo = target.repo
    
    commit_file = Path(args.commit_file) if args.commit_file else DEFAULT_COMMIT_FILE
    if not commit_file.is_absolute():
        commit_file = (Path.cwd() / commit_file).resolve()
    commit_entries = load_commits(commit_file)

    if not commit_entries:
        logger.warning("No commits found in {}", commit_file)
        return

    default_output = "/root/code_check/commit_to_test_cases/linux_kernel_test_cases"
    output_root = Path(args.output_dir) if args.output_dir else Path(default_output)
    output_root.mkdir(parents=True, exist_ok=True)

    
    for commit_sha, bug_type in commit_entries:
        process_commit(repo, commit_sha, bug_type, output_root)


if __name__ == "__main__":
    main()