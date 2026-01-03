import json
from pathlib import Path
from typing import Dict, List, Optional

from agents.patch_agent import PatchAnalysisAgent, PatchPattern
from agents.search_agent import SearchAgent
from agents.slice_agent import SliceAgent
from agents.verification_agent import VerificationAgent
from utils.json_utils import dump_pretty_json
# from loggru import logger
_SUPPORTED_EXTENSIONS = {
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".cxx",
    ".hpp",
    ".hh",
}


class StageOnePipeline:
    """Coordinate multi-agent collaboration for test case extraction."""

    def __init__(self, llm, max_attempts: int = 3) -> None:
        self.patch_agent = PatchAnalysisAgent(llm)
        self.slice_agent = SliceAgent(llm)
        self.search_agent = SearchAgent(llm)
        self.verify_agent = VerificationAgent()
        self.max_attempts = max_attempts

    def run(self, commit_dir: Path, file_filters: Optional[List[str]] = None) -> Dict:
        commit_dir = commit_dir.resolve()
        patch_md = (commit_dir / "patch.md").read_text(encoding="utf-8")
        metadata_path = commit_dir / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        pattern = self.patch_agent.analyze(patch_md)

        stage1_dir = commit_dir / "stage1"
        buggy_dir = stage1_dir / "buggy_case"
        fixed_dir = stage1_dir / "fixed_case"
        result_dir = commit_dir / "test_case_result"
        for directory in (buggy_dir, fixed_dir, result_dir):
            directory.mkdir(parents=True, exist_ok=True)

        processed_files: List[Dict] = []
        for file_meta in metadata.get("files", []):
            rel_path = file_meta.get("new_path") or file_meta.get("old_path")
            if not rel_path:
                continue
            if file_filters and rel_path not in file_filters:
                continue
            if Path(rel_path).suffix.lower() not in _SUPPORTED_EXTENSIONS:
                continue
            before_rel = file_meta.get("before_file")
            after_rel = file_meta.get("after_file")
            if not before_rel or not after_rel:
                continue
            before_path = commit_dir / before_rel
            after_path = commit_dir / after_rel
            if not before_path.exists() or not after_path.exists():
                continue
            suffix = Path(rel_path).suffix or ".c"
            safe_base = rel_path.replace("/", "__").replace("\\", "__")
            buggy_output = buggy_dir / f"{safe_base}_bug{suffix}"
            fixed_output = fixed_dir / f"{safe_base}_fix{suffix}"
            patch_file = file_meta.get("patch_file")
            diff_text = ""
            if patch_file:
                diff_path = commit_dir / patch_file
                if diff_path.exists():
                    diff_text = diff_path.read_text(encoding="utf-8")

            buggy_info = self._generate_buggy_case(
                pattern,
                before_path,
                buggy_output,
                diff_text,
            )
            fixed_info = self._generate_fixed_case(
                pattern,
                after_path,
                fixed_output,
                diff_text,
            )

            self._persist_success_case(buggy_output, result_dir / buggy_output.name)
            self._persist_success_case(fixed_output, result_dir / fixed_output.name)

            processed_files.append(
                {
                    "relative_path": rel_path,
                    "buggy_case": str(buggy_output.relative_to(commit_dir)),
                    "fixed_case": str(fixed_output.relative_to(commit_dir)),
                    "buggy_compile_log": buggy_info["compile_log"],
                    "fixed_compile_log": fixed_info["compile_log"],
                    "buggy_stubs": buggy_info["stubs"],
                    "fixed_stubs": fixed_info["stubs"],
                }
            )

        report = {
            "pattern": pattern.to_dict(),
            "files": processed_files,
        }
        dump_pretty_json(stage1_dir / "report.json", report)
        return report

    def _generate_buggy_case(
        self,
        pattern: PatchPattern,
        source_path: Path,
        output_path: Path,
        diff_text: str,
    ) -> Dict:
        before_text = source_path.read_text(encoding="utf-8")
        compile_feedback = None
        stubs_used: List[str] = []
        for attempt in range(self.max_attempts):
            slice_result = self.slice_agent.create_buggy_slice(
                pattern.description,
                before_text,
                ", ".join(pattern.key_apis) or "",
                diff_text,
                compile_feedback,
            )
            enriched = self.search_agent.enrich_with_stubs(
                slice_result.code,
                before_text,
                pattern.description,
                compile_feedback,
                allowed_symbols=pattern.key_apis,
            )
            if enriched.added_functions:
                stubs_used.extend(enriched.added_functions)
            output_path.write_text(enriched.updated_code, encoding="utf-8")
            verification = self.verify_agent.verify(output_path)
            if verification.success:
                return {
                    "compile_log": verification.log,
                    "stubs": stubs_used,
                }
            compile_feedback = verification.log
        raise RuntimeError(f"Failed to compile buggy case for {source_path}")

    def _generate_fixed_case(
        self,
        pattern: PatchPattern,
        source_path: Path,
        output_path: Path,
        diff_text: str,
    ) -> Dict:
        after_text = source_path.read_text(encoding="utf-8")
        compile_feedback = None
        stubs_used: List[str] = []
        for attempt in range(self.max_attempts):
            print(f"Fixed case attempt {attempt + 1} for {source_path}")
            slice_result = self.slice_agent.create_fixed_slice(
                pattern.description,
                after_text,
                ", ".join(pattern.key_apis) or "",
                diff_text,
            )
            enriched = self.search_agent.enrich_with_stubs(
                slice_result.code,
                after_text,
                pattern.description,
                compile_feedback,
                allowed_symbols=pattern.key_apis,
            )
            if enriched.added_functions:
                stubs_used.extend(enriched.added_functions)
            output_path.write_text(enriched.updated_code, encoding="utf-8")
            print(f"Verifying fixed case at {output_path}")
            print(f"Fixed case code:\n{enriched.updated_code}")
            verification = self.verify_agent.verify(output_path)
            if verification.success:
                return {
                    "compile_log": verification.log,
                    "stubs": stubs_used,
                }
            compile_feedback = verification.log
        raise RuntimeError(f"Failed to compile fixed case for {source_path}")

    @staticmethod
    def _persist_success_case(source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
