"""Collect CodeQL imports from .qll files.

This script recursively walks the directory
/root/code_check/codeql/cpp/ql/lib/semmle/code/cpp and its subdirectories,
skipping any directory named "internal", and converts each found
.qll file path into a CodeQL import statement.

Example:
  /root/code_check/codeql/cpp/ql/lib/semmle/code/cpp/controlflow/ControlFlowGraph.qll
  -> semmle/code/cpp/controlflow/ControlFlowGraph.qll
  -> import semmle.code.cpp.controlflow.ControlFlowGraph

The resulting import statements are written to `codeql_imports.txt`
next to this script (one import per line).
"""

from pathlib import Path
import sys


BASE_ROOT = Path("/root/code_check/codeql/cpp/ql/lib")
TARGET_DIR = BASE_ROOT / "semmle" / "code" / "cpp"
OUTFILE = Path(__file__).parent / "codeql_imports.txt"


def collect_codeql_imports(base_root: Path, target_dir: Path):
	"""Return a sorted list of import statements for all .qll files.

	- Skips any file that has an "internal" directory in its relative path
	  under `target_dir`.
	- Produces import lines like: `import semmle.code.cpp.controlflow.BasicBlocks`
	"""
	if not target_dir.exists():
		raise FileNotFoundError(f"Target directory does not exist: {target_dir}")

	imports = set()
	for p in target_dir.rglob("*.qll"):
		# Skip any path that contains a folder named 'internal' under target_dir
		try:
			rel_to_target = p.relative_to(target_dir)
		except Exception:
			# should not happen, but be robust
			rel_to_target = p
		if "internal" in rel_to_target.parts:
			continue

		# Compute relative path starting at base_root, e.g. 'semmle/code/cpp/...'
		try:
			rel = p.relative_to(base_root)
		except Exception:
			# If a file is not under base_root for some reason, skip it
			continue

		rel_posix = rel.as_posix()
		if rel_posix.lower().endswith(".qll"):
			module_path = rel_posix[:-4]
		else:
			module_path = rel_posix

		module = module_path.replace("/", ".")
		imports.add(f"import {module}")

	return sorted(imports)


def main() -> int:
	try:
		imports = collect_codeql_imports(BASE_ROOT, TARGET_DIR)
	except FileNotFoundError as e:
		print(str(e), file=sys.stderr)
		return 2

	OUTFILE.write_text("\n".join(imports) + ("\n" if imports else ""), encoding="utf-8")
	print(f"Wrote {len(imports)} imports to {OUTFILE}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

