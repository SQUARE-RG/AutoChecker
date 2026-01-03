import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from llm_interface.llm_provider import llm_client
from pipelines.stage_one_pipeline import StageOnePipeline
from pipelines.stage_two_pipeline import StageTwoPipeline


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description=(
			"Multi-agent test case extraction pipeline. "
			"Currently supports Stage-1 (buggy/fixed slice generation)."
		)
	)
	parser.add_argument(
		"--commit-dir",
		# required=True,
		default="/root/code_check/commit_to_test_cases/linux_kernel_test_cases/1f886a7bfb3faf4c1021e73f045538008ce7634e-Null-Pointer-Dereference",
		help="Path to the commit bundle (contains metadata.json, before/, after/, patch.md).",
	)
	parser.add_argument(
		"--files",
		nargs="*",
		default=None,
		help="Optional list of repo-relative file paths to process (defaults to all C/C++ files).",
	)
	parser.add_argument(
		"--max-attempts",
		type=int,
		default=3,
		help="Maximum attempts per case when trying to reach a compiling slice.",
	)
	parser.add_argument(
		"--stage",
		choices=["stage1", "stage2"],
		default="stage2",
		help="Select which pipeline to run: stage1 extraction or stage2 generalization.",
	)
	return parser


def main() -> None:
	load_dotenv()
	parser = build_parser()
	args = parser.parse_args()
	if llm_client is None:
		raise RuntimeError("LLM client is not configured. Check MODEL_NAME and related API keys.")

	commit_dir = Path(args.commit_dir)
	if args.stage == "stage1":
		pipeline = StageOnePipeline(llm_client, max_attempts=args.max_attempts)
		report = pipeline.run(commit_dir, file_filters=args.files)
	else:
		pipeline = StageTwoPipeline(llm_client)
		report = pipeline.run(commit_dir)
	print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
	main()

