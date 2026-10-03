import csv
import os
import argparse
import subprocess
from pathlib import Path
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import logging
sys.path.append(str(Path(__file__).parent.parent))
from src.config import PROJECT_INFO,LOGS_DIR,CVES_PATH

# Setup logging
def setup_logging():
    log_dir = LOGS_DIR
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'codeql_build_dbs_{time.strftime("%Y%m%d_%H%M%S")}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

def find_project_source_directory(cve_base_path):
    cve_name = os.path.basename(cve_base_path)

    # Look for project directories (not CVE-specific dirs or files)
    for item in os.listdir(cve_base_path):
        item_path = os.path.join(cve_base_path, item)

        # Skip CVE-specific directories and files
        if item.startswith(cve_name) or item.endswith('.diff'):
            continue

        # Look for directories that contain Java source
        if os.path.isdir(item_path):
            # Check if this directory contains pom.xml, build.gradle, or build.xml (indicating it's a project root)
            if (os.path.exists(os.path.join(item_path, "pom.xml")) or
                os.path.exists(os.path.join(item_path, "build.gradle")) or
                os.path.exists(os.path.join(item_path, "build.gradle.kts")) or
                os.path.exists(os.path.join(item_path, "build.xml"))):
                return item_path

            # Also check if it has Java source files
            for root, dirs, files in os.walk(item_path):
                if any(f.endswith('.java') for f in files):
                    return item_path
                break  

    return None

def checkout_commit(project_source, commit_hash):
    logger = logging.getLogger(__name__)
    try:
        msg = f"Checking out commit {commit_hash[:8]} in {project_source}"
        print(msg)
        logger.info(msg)

        stash_result = subprocess.run([
            'git', 'stash', 'push', '-m', f'Auto-stash before checkout {commit_hash[:8]}'
        ], cwd=project_source, capture_output=True, text=True, timeout=30)

        if stash_result.returncode == 0:
            logger.info(f"Stashed changes before checkout of {commit_hash[:8]}")
        else:
            logger.debug(f"Stash result for {commit_hash[:8]}: {stash_result.stderr}")

        result = subprocess.run([
            'git', 'checkout', commit_hash
        ], cwd=project_source, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            msg = f"Successfully checked out commit {commit_hash[:8]}"
            print(msg)
            logger.info(msg)
            return True
        else:
            msg = f"Failed to checkout commit {commit_hash[:8]}: {result.stderr}"
            print(msg)
            logger.error(msg)
            return False
    except subprocess.TimeoutExpired:
        msg = f"Timeout checking out commit {commit_hash[:8]}"
        print(msg)
        logger.error(msg)
        return False
    except Exception as e:
        msg = f"Error checking out commit {commit_hash[:8]}: {e}"
        print(msg)
        logger.error(msg)
        return False

def create_codeql_database(cve_dir_path, version_type, cve_base_path, commit_hash=None):
    """Create CodeQL database using build-mode=none (no build required)"""
    logger = logging.getLogger(__name__)

    db_java_path = os.path.join(cve_dir_path, "db-java")
    if os.path.exists(db_java_path):
        print(f"Database already exists at {db_java_path}")
        return True

    database_path = os.path.abspath(cve_dir_path)

    project_source = find_project_source_directory(cve_base_path)

    if commit_hash and project_source:
        if not checkout_commit(project_source, commit_hash):
            print(f"Failed to checkout commit {commit_hash} - aborting database creation")
            return False

    if project_source:
        source_path = project_source
        print(f"Found project source directory: {source_path}")
    else:
        source_candidates = [
            os.path.join(cve_dir_path, "src"),
            os.path.join(cve_dir_path, "src/main/java"),
            cve_dir_path
        ]

        source_path = cve_dir_path 
        for candidate in source_candidates:
            if os.path.exists(candidate):
                source_path = candidate
                break
        print(f"Using fallback source path: {source_path}")

    command = [
        "codeql", "database", "create",
        database_path,
        "--source-root", source_path,
        "--language", "java",
        "--build-mode=none",
        "--overwrite"
    ]

    try:
        print(f"Creating database at: {database_path}")
        print(f"Using source path: {source_path}")
        print(f"Using build-mode=none (no build required)")

        res = subprocess.run(command, capture_output=True, text=True, timeout=1800)  # 10 min timeout

        if res.returncode == 0:
            print(f"Successfully created CodeQL database")
            logger.info(f"Database creation successful: {database_path}")
            return True
        else:
            print(f"CodeQL database creation failed")
            print(f"Stdout: {res.stdout}")
            print(f"Stderr: {res.stderr}")
            logger.error(f"Database creation failed: {res.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"Timeout during CodeQL database creation")
        logger.error(f"Database creation timeout: {database_path}")
        return False
    except Exception as e:
        print(f"Exception during CodeQL database creation: {e}")
        logger.error(f"Database creation exception: {e}")
        return False

def load_cve_data():
    cve_data = {}
    with open(PROJECT_INFO, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cve_data[row['cve_id']] = row
    return cve_data

def get_latest_commit(repo_path, commit_ids):
    """Get the latest commit from a list of commit IDs based on commit timestamp."""
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
        except (subprocess.CalledProcessError, ValueError):
            continue

    return latest_commit

def find_repo_directory(cve_dir_path, cve_id):
    """Find the repository directory within a CVE directory."""
    for item in os.listdir(cve_dir_path):
        item_path = os.path.join(cve_dir_path, item)
        # Skip CVE-specific files and directories
        if item.startswith(cve_id) or item.endswith('.diff'):
            continue
        # Check if it's a git repository
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '.git')):
            return item_path
    return None

def process_cve_directory(cve_dir_path):
    cve_id = os.path.basename(cve_dir_path)
    logger = logging.getLogger(__name__)
    print(f"\n{'='*60}")
    print(f"Processing {cve_id}...")
    print(f"{'='*60}")

    cve_data = load_cve_data()
    if cve_id not in cve_data:
        print(f"CVE {cve_id} not found in project_info.csv")
        return [f"{cve_id}: Not found in CSV"]

    cve_info = cve_data[cve_id]
    buggy_commit = cve_info['buggy_commit_id']
    fix_commit_ids_str = cve_info['fix_commit_ids']

    if not buggy_commit:
        print(f"No buggy commit specified for {cve_id}")
        return [f"{cve_id}: No buggy commit"]

    if not fix_commit_ids_str:
        print(f"No fix commits specified for {cve_id}")
        return [f"{cve_id}: No fix commits"]

    # Find the repository directory
    repo_path = find_repo_directory(cve_dir_path, cve_id)
    if not repo_path:
        print(f"Repository not found in {cve_dir_path}")
        return [f"{cve_id}: Repository not found"]

    print(f"Found repository: {repo_path}")

    # Parse fix commits and get the latest one
    fix_commit_ids = [c.strip() for c in fix_commit_ids_str.split(';') if c.strip()]
    if len(fix_commit_ids) > 1:
        print(f"Multiple fix commits found ({len(fix_commit_ids)}), selecting latest...")
        fix_commit = get_latest_commit(repo_path, fix_commit_ids)
        if not fix_commit:
            fix_commit = fix_commit_ids[-1]  # Fallback to last one
        print(f"Selected fix commit: {fix_commit[:8]}")
    else:
        fix_commit = fix_commit_ids[0]

    # Database paths
    vul_db_path = os.path.join(cve_dir_path, f"{cve_id}-vul")
    fix_db_path = os.path.join(cve_dir_path, f"{cve_id}-fix")

    vul_db_exists = os.path.exists(os.path.join(vul_db_path, "db-java"))
    fix_db_exists = os.path.exists(os.path.join(fix_db_path, "db-java"))

    if vul_db_exists and fix_db_exists:
        print(f"{cve_id} already has complete databases, skipping...")
        return [f"{cve_id}-vul: Already exists", f"{cve_id}-fix: Already exists"]

    results = []

    # Create vulnerable version database
    if not vul_db_exists:
        print(f"\nCreating vulnerable database for {cve_id}...")
        print(f"Checking out buggy commit: {buggy_commit[:8]}")
        if checkout_commit(repo_path, buggy_commit):
            success = create_codeql_database(vul_db_path, "vul", cve_dir_path, None)
            if success:
                results.append(f"{cve_id}-vul: Success")
            else:
                results.append(f"{cve_id}-vul: Database creation failed")
        else:
            results.append(f"{cve_id}-vul: Checkout failed")
    else:
        print(f"Vulnerable database already exists for {cve_id}")
        results.append(f"{cve_id}-vul: Already exists")

    # Create fixed version database
    if not fix_db_exists:
        print(f"\nCreating fixed database for {cve_id}...")
        print(f"Checking out fix commit: {fix_commit[:8]}")
        if checkout_commit(repo_path, fix_commit):
            success = create_codeql_database(fix_db_path, "fix", cve_dir_path, None)
            if success:
                results.append(f"{cve_id}-fix: Success")
            else:
                results.append(f"{cve_id}-fix: Database creation failed")
        else:
            results.append(f"{cve_id}-fix: Checkout failed")
    else:
        print(f"Fixed database already exists for {cve_id}")
        results.append(f"{cve_id}-fix: Already exists")

    # Checkout back to buggy commit (leave repo in vulnerable state)
    checkout_commit(repo_path, buggy_commit)

    return results

def process_cve_directory_parallel(cve_dir_path):
    """Wrapper function for parallel processing"""
    return process_cve_directory(cve_dir_path)

def main():
    # Setup logging first
    logger = setup_logging()
    logger.info("Starting CodeQL database creation process (build-mode=none)")

    parser = argparse.ArgumentParser(description='Create CodeQL databases using build-mode=none')
    parser.add_argument('--cve-dir', help='Path to CVE directory',
                       default=CVES_PATH)
    parser.add_argument('--cve-id', help='Specific CVE ID to process', default=None)
    parser.add_argument('--parallel', action='store_true', help='Enable parallel processing')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum number of parallel workers (default: 4)')
    args = parser.parse_args()

    # Get the CVE base directory
    cve_base_dir = args.cve_dir

    start_time = time.time()

    print(f"\nUsing build-mode=none (no Java build required)")
    print(f"CVE base directory: {cve_base_dir}")

    all_results = []

    if args.cve_id:
        # Process specific CVE
        cve_path = os.path.join(cve_base_dir, args.cve_id)
        if os.path.exists(cve_path):
            results = process_cve_directory(cve_path)
            all_results.extend(results)
            print("\nResults:")
            for result in results:
                print(f"  {result}")
        else:
            print(f"CVE directory not found: {cve_path}")
    else:
        # Process all CVE directories in the base path
        cve_dirs = []
        for item in os.listdir(cve_base_dir):
            if item.startswith('CVE-') and os.path.isdir(os.path.join(cve_base_dir, item)):
                cve_path = os.path.join(cve_base_dir, item)
                cve_dirs.append(cve_path)

        if not cve_dirs:
            print(f"No CVE directories found in {cve_base_dir}")
        else:
            print(f"Found {len(cve_dirs)} CVE directories to process")

            if args.parallel:
                print(f"Using parallel processing with {args.max_workers} workers")

                with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
                    # Submit all tasks
                    future_to_cve = {executor.submit(process_cve_directory_parallel, cve_dir): cve_dir
                                   for cve_dir in cve_dirs}

                    # Process completed tasks
                    completed = 0
                    for future in as_completed(future_to_cve):
                        cve_path = future_to_cve[future]
                        cve_id = os.path.basename(cve_path)
                        completed += 1

                        try:
                            results = future.result()
                            all_results.extend(results)
                            print(f"[{completed}/{len(cve_dirs)}] Completed {cve_id}")
                        except Exception as e:
                            print(f"[{completed}/{len(cve_dirs)}] Failed {cve_id}: {e}")
                            all_results.append(f"{cve_id}: Exception - {str(e)}")

            else:
                # Sequential processing
                print("Using sequential processing")
                for i, cve_path in enumerate(cve_dirs, 1):
                    cve_id = os.path.basename(cve_path)
                    print(f"\n[{i}/{len(cve_dirs)}] Processing {cve_id}")
                    results = process_cve_directory(cve_path)
                    all_results.extend(results)

    # Print final summary
    print("\n" + "="*50)
    print("FINAL PROCESSING SUMMARY")
    print("="*50)
    success_count = sum(1 for r in all_results if "Success" in r)
    error_count = sum(1 for r in all_results if "failed" in r)
    already_exists_count = sum(1 for r in all_results if "Already exists" in r)
    not_found_count = sum(1 for r in all_results if "not found" in r)

    print(f"Total databases: {len(all_results)}")
    print(f"Successful: {success_count}")
    print(f"Already existed: {already_exists_count}")
    print(f"Failed: {error_count}")
    print(f"Not found: {not_found_count}")

    if error_count > 0:
        print("\nFailed databases:")
        for result in all_results:
            if "failed" in result:
                print(f"  {result}")

    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
