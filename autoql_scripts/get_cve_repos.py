#!/usr/bin/env python3
"""
Generate diffs between vulnerable and fixed commits for CVEs.

This script reads CVE information from project_info.csv, clones the relevant
repositories, and generates diff files showing the changes between vulnerable
and fixed commits.

Usage:
    # Process a single CVE
    python get_cve_repos.py --cve CVE-2018-9159

    # Process multiple CVEs (comma-separated)
    python get_cve_repos.py --cves CVE-2018-9159,CVE-2016-9177

    # Process CVEs from a file (one CVE ID per line)
    python get_cve_repos.py --cve-file cves.txt

    # Process all CVEs
    python get_cve_repos.py --all

    # Force regenerate existing diffs
    python get_cve_repos.py --cve CVE-2018-9159 --force
"""

import os
import sys
import csv
import argparse
import subprocess
import selectors
from typing import List, Dict, Optional, Sequence

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import PROJECT_INFO, CVES_PATH


def stream_git_command(
    cmd: Sequence[str],
    cwd: Optional[str] = None,
    prefix: str = "",
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Run a git command and stream progress output live.

    Git usually writes clone/fetch progress to stderr with carriage returns,
    so we stream both stdout and stderr and flush on either newline or CR.
    """
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,
    )

    selector = selectors.DefaultSelector()
    buffers = {}

    if process.stdout is not None:
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        buffers["stdout"] = ""
    if process.stderr is not None:
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        buffers["stderr"] = ""

    stdout_chunks: List[str] = []
    stderr_chunks: List[str] = []

    while selector.get_map():
        for key, _ in selector.select():
            stream = key.fileobj
            stream_name = key.data
            chunk = stream.read(1)

            if chunk == "":
                remaining = buffers[stream_name]
                if remaining:
                    line = f"{prefix}{remaining}" if prefix else remaining
                    print(line, flush=True)
                    if stream_name == "stdout":
                        stdout_chunks.append(remaining)
                    else:
                        stderr_chunks.append(remaining)
                selector.unregister(stream)
                stream.close()
                continue

            buffers[stream_name] += chunk

            if chunk in ("\n", "\r"):
                text = buffers[stream_name].rstrip("\r\n")
                if text:
                    line = f"{prefix}{text}" if prefix else text
                    print(line, flush=True)
                    if stream_name == "stdout":
                        stdout_chunks.append(text + "\n")
                    else:
                        stderr_chunks.append(text + "\n")
                buffers[stream_name] = ""

    returncode = process.wait()
    stdout_text = "".join(stdout_chunks)
    stderr_text = "".join(stderr_chunks)

    if check and returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=returncode,
            cmd=list(cmd),
            output=stdout_text,
            stderr=stderr_text,
        )

    return subprocess.CompletedProcess(
        args=list(cmd),
        returncode=returncode,
        stdout=stdout_text,
        stderr=stderr_text,
    )


def load_project_info() -> Dict[str, Dict]:
    """Load CVE project information from CSV file."""
    cve_data = {}
    with open(PROJECT_INFO, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cve_id = row['cve_id']
            cve_data[cve_id] = {
                'github_username': row['github_username'],
                'github_repository_name': row['github_repository_name'],
                'github_url': row['github_url'],
                'buggy_commit_id': row['buggy_commit_id'],
                'fix_commit_ids': row['fix_commit_ids'].split(';') if row['fix_commit_ids'] else []
            }
    return cve_data


def get_latest_commit(repo_path: str, commit_ids: List[str]) -> Optional[str]:
    """
    Get the latest commit from a list of commit IDs based on commit timestamp.

    Args:
        repo_path: Path to the git repository
        commit_ids: List of commit SHA hashes

    Returns:
        The commit ID with the most recent timestamp, or None if none found
    """
    if not commit_ids:
        return None

    if len(commit_ids) == 1:
        return commit_ids[0]

    latest_commit = None
    latest_timestamp = 0

    for commit_id in commit_ids:
        try:
            result = subprocess.run(
                ['git', 'show', '-s', '--format=%ct', commit_id],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            timestamp = int(result.stdout.strip())
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_commit = commit_id
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"  Warning: Could not get timestamp for commit {commit_id}: {e}")
            continue

    return latest_commit


def clone_repository(github_url: str, clone_dir: str) -> bool:
    """
    Clone a git repository.

    Args:
        github_url: URL of the GitHub repository
        clone_dir: Directory to clone into

    Returns:
        True if successful, False otherwise
    """
    clone_cmd = [
        'git', 'clone',
        '--filter=blob:none',
        '--no-checkout',
        '--progress',
        '--no-tags',
        github_url,
        clone_dir,
    ]

    try:
        stream_git_command(clone_cmd, prefix="    [clone] ")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Partial clone failed, falling back to full clone...")
        if os.path.exists(clone_dir):
            subprocess.run(['rm', '-rf', clone_dir], check=False)

        try:
            stream_git_command(
                ['git', 'clone', '--progress', '--no-tags', github_url, clone_dir],
                prefix="    [clone] "
            )
            return True
        except subprocess.CalledProcessError as fallback_error:
            print(f"  Error cloning repository: {fallback_error.stderr or e.stderr}")
            return False


def fetch_commit(repo_path: str, commit_id: str) -> bool:
    """Try to fetch a specific commit with live progress output."""
    try:
        stream_git_command(
            ['git', 'fetch', '--progress', '--no-tags', 'origin', commit_id],
            cwd=repo_path,
            prefix=f"    [fetch {commit_id[:12]}] "
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Warning: targeted fetch failed for {commit_id[:12]}: {e.stderr.strip() or e}")
        return False


def fetch_all_refs(repo_path: str) -> bool:
    """Fallback fetch for cases where targeted commit fetch is not enough."""
    try:
        stream_git_command(
            ['git', 'fetch', '--all', '--tags', '--progress'],
            cwd=repo_path,
            prefix="    [fetch-all] "
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Warning: full fetch failed: {e.stderr.strip() or e}")
        return False


def ensure_commits_available(repo_path: str, commit_ids: List[str]) -> bool:
    """Ensure all requested commits exist locally, using targeted fetch first."""
    missing_commits = []

    for commit_id in commit_ids:
        result = subprocess.run(
            ['git', 'cat-file', '-e', f'{commit_id}^{{commit}}'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            missing_commits.append(commit_id)

    if not missing_commits:
        return True

    print(f"  Ensuring {len(missing_commits)} required commit(s) are available locally...")
    targeted_fetch_ok = True
    for commit_id in missing_commits:
        if not fetch_commit(repo_path, commit_id):
            targeted_fetch_ok = False
            break

    if targeted_fetch_ok:
        still_missing = []
        for commit_id in missing_commits:
            result = subprocess.run(
                ['git', 'cat-file', '-e', f'{commit_id}^{{commit}}'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                still_missing.append(commit_id)
        if not still_missing:
            return True
        missing_commits = still_missing

    print("  Targeted fetch was insufficient, falling back to fetching repository refs...")
    if not fetch_all_refs(repo_path):
        return False

    for commit_id in missing_commits:
        result = subprocess.run(
            ['git', 'cat-file', '-e', f'{commit_id}^{{commit}}'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  Error: commit still unavailable after fallback fetch: {commit_id}")
            return False

    return True


def generate_diff(repo_path: str, vulnerable_commit: str, fix_commit: str) -> Optional[str]:
    """
    Generate a diff between vulnerable and fixed commits.

    Args:
        repo_path: Path to the git repository
        vulnerable_commit: SHA of the vulnerable commit
        fix_commit: SHA of the fix commit

    Returns:
        The diff as a string, or None if failed
    """
    try:
        result = subprocess.run(
            ['git', 'diff', vulnerable_commit, fix_commit],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        return result.stdout.decode('utf-8', errors='replace')
    except subprocess.CalledProcessError as e:
        print(f"  Error generating diff: {e.stderr}")
        return None


def process_cve(cve_id: str, cve_info: Dict, force: bool = False) -> bool:
    """
    Process a single CVE: clone repo, generate diff, save to file.

    Args:
        cve_id: The CVE identifier
        cve_info: Dictionary containing CVE project information
        force: Whether to regenerate even if files already exist

    Returns:
        True if successful, False otherwise
    """
    print(f"\nProcessing {cve_id}...")

    # Create CVE directory
    cve_dir = os.path.join(CVES_PATH, cve_id)
    os.makedirs(cve_dir, exist_ok=True)

    diff_file = os.path.join(cve_dir, f"{cve_id}.diff")
    repo_name = cve_info['github_repository_name']
    repo_dir = os.path.join(cve_dir, repo_name)

    github_url = cve_info['github_url']
    vulnerable_commit = cve_info['buggy_commit_id']
    fix_commits = cve_info['fix_commit_ids']

    if not vulnerable_commit:
        print(f"  Error: No vulnerable commit specified for {cve_id}")
        return False

    if not fix_commits:
        print(f"  Error: No fix commits specified for {cve_id}")
        return False

    # Check if already complete
    if not force and os.path.exists(diff_file) and os.path.exists(repo_dir):
        print(f"  Already complete (diff and repo exist)")
        return True

    # Clone repository into CVE directory if not present
    if not os.path.exists(repo_dir):
        print(f"  Cloning {github_url} into {repo_dir}...")
        if not clone_repository(github_url, repo_dir):
            return False
    else:
        print(f"  Repository already exists: {repo_dir}")

    # Get the latest fix commit
    if len(fix_commits) > 1:
        if not ensure_commits_available(repo_dir, [vulnerable_commit] + fix_commits):
            return False
        print(f"  Multiple fix commits found ({len(fix_commits)}), selecting latest...")
        fix_commit = get_latest_commit(repo_dir, fix_commits)
        if not fix_commit:
            print(f"  Error: Could not determine latest fix commit")
            return False
        print(f"  Selected fix commit: {fix_commit[:12]}")
    else:
        fix_commit = fix_commits[0]

    if not ensure_commits_available(repo_dir, [vulnerable_commit, fix_commit]):
        return False

    # Generate diff
    if not os.path.exists(diff_file) or force:
        print(f"  Generating diff: {vulnerable_commit[:12]} -> {fix_commit[:12]}")
        diff_content = generate_diff(repo_dir, vulnerable_commit, fix_commit)

        if diff_content is None:
            return False

        if not diff_content.strip():
            print(f"  Warning: Empty diff generated")

        # Save diff to file
        with open(diff_file, 'w', encoding='utf-8') as f:
            f.write(diff_content)
        print(f"  Saved diff to: {diff_file}")
    else:
        print(f"  Diff file already exists: {diff_file}")

    # Checkout the vulnerable commit in the repo
    print(f"  Checking out vulnerable commit: {vulnerable_commit[:12]}")
    try:
        stream_git_command(
            ['git', 'checkout', '--progress', vulnerable_commit],
            cwd=repo_dir,
            prefix="    [checkout] "
        )
    except subprocess.CalledProcessError as e:
        print(f"  Warning: Could not checkout vulnerable commit: {e.stderr}")

    print(f"  Complete: {cve_dir}")
    return True


def process_cves(cve_ids: List[str], cve_data: Dict[str, Dict],
                 force: bool = False) -> Dict[str, bool]:
    """
    Process multiple CVEs.

    Args:
        cve_ids: List of CVE identifiers to process
        cve_data: Dictionary of all CVE project information
        force: Whether to regenerate even if files already exist

    Returns:
        Dictionary mapping CVE IDs to success status
    """
    results = {}

    for cve_id in cve_ids:
        if cve_id not in cve_data:
            print(f"\nWarning: {cve_id} not found in project_info.csv")
            results[cve_id] = False
            continue

        success = process_cve(cve_id, cve_data[cve_id], force=force)
        results[cve_id] = success

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Generate diffs between vulnerable and fixed commits for CVEs'
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--cve',
        type=str,
        help='Process a single CVE (e.g., CVE-2018-9159)'
    )
    group.add_argument(
        '--cves',
        type=str,
        help='Process multiple CVEs, comma-separated (e.g., CVE-2018-9159,CVE-2016-9177)'
    )
    group.add_argument(
        '--cve-file',
        type=str,
        help='Process CVEs from a file (one CVE ID per line)'
    )
    group.add_argument(
        '--all',
        action='store_true',
        help='Process all CVEs in project_info.csv'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate diffs even if they already exist'
    )

    args = parser.parse_args()

    # Load CVE data
    print("Loading project information...")
    cve_data = load_project_info()
    print(f"Loaded {len(cve_data)} CVEs from {PROJECT_INFO}")

    # Determine which CVEs to process
    if args.cve:
        cve_ids = [args.cve]
    elif args.cves:
        cve_ids = [cve.strip() for cve in args.cves.split(',')]
    elif args.cve_file:
        with open(args.cve_file, 'r', encoding='utf-8') as f:
            cve_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:  # args.all
        cve_ids = list(cve_data.keys())

    print(f"\nWill process {len(cve_ids)} CVE(s)")

    if args.force:
        print("Force mode enabled - will regenerate existing diffs")

    # Process CVEs
    results = process_cves(cve_ids, cve_data, force=args.force)

    # Print summary
    successful = sum(1 for success in results.values() if success)
    failed = len(results) - successful

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total CVEs processed: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    if failed > 0:
        print("\nFailed CVEs:")
        for cve_id, success in results.items():
            if not success:
                print(f"  - {cve_id}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
