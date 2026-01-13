import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from agents.generalization_agent import GeneratedCase, TestCaseGeneralizationAgent
from agents.verification_agent import VerificationAgent
from utils.json_utils import dump_pretty_json


class StageTwoPipeline:
    """Handle large-scale test case generalization for both buggy and fixed variants."""

    def __init__(
        self,
        llm,
        cases_per_variant: int = 10,
        max_repairs: int = 2,
    ) -> None:
        self.generalization_agent = TestCaseGeneralizationAgent(llm)
        self.verification_agent = VerificationAgent()
        self.cases_per_variant = cases_per_variant
        self.max_repairs = max_repairs

    def run(self, commit_dir: Path) -> Dict:
        commit_dir = commit_dir.resolve()
        stage1_report = json.loads((commit_dir / "stage1" / "report.json").read_text(encoding="utf-8"))
        pattern_info = stage1_report.get("pattern", {})
        trigger_desc = pattern_info.get("trigger_conditions") or pattern_info.get("description", "")
        base_cases_dir = commit_dir / "test_case_result"
        buggy_exemplar, fixed_exemplar = self._locate_stage1_examples(base_cases_dir)
        if buggy_exemplar is None or fixed_exemplar is None:
            raise FileNotFoundError("无法在 test_case_result 中找到第一阶段生成的基准测试用例。")

        stage2_dir = commit_dir / "stage2"
        buggy_output_dir = base_cases_dir / "stage2" / "buggy_cases"
        fixed_output_dir = base_cases_dir / "stage2" / "fixed_cases"
        for directory in (stage2_dir, buggy_output_dir, fixed_output_dir):
            directory.mkdir(parents=True, exist_ok=True)

        buggy_cases = self.generalization_agent.generate_cases(
            trigger_desc,
            buggy_exemplar.read_text(encoding="utf-8"),
            "buggy",
            self.cases_per_variant,
            "确保每个示例都保留漏洞并包含 // CHECK-MESSAGES 注释。",
        )
        print("the amount of buggy cases:", len(buggy_cases))
        fixed_cases = self.generalization_agent.generate_cases(
            trigger_desc,
            fixed_exemplar.read_text(encoding="utf-8"),
            "fixed",
            self.cases_per_variant,
            "修复后的测试用例如无漏洞，不要包含 // CHECK-MESSAGES 注释。",
        )
        print("the amount of fixed cases:", len(fixed_cases))
        buggy_report = self._process_cases(
            trigger_desc,
            buggy_cases,
            buggy_output_dir,
            commit_dir,
            variant="buggy",
        )
        fixed_report = self._process_cases(
            trigger_desc,
            fixed_cases,
            fixed_output_dir,
            commit_dir,
            variant="fixed",
        )

        summary = {
            "pattern": trigger_desc,
            "buggy": buggy_report,
            "fixed": fixed_report,
        }
        dump_pretty_json(stage2_dir / "report.json", summary)
        return summary

    def _process_cases(
        self,
        pattern: str,
        cases: List[GeneratedCase],
        output_dir: Path,
        commit_dir: Path,
        variant: str,
    ) -> List[Dict]:
        variant_suffix = "bug" if variant == "buggy" else "fix"
        processed: List[Dict] = []
        success_counter = 0
        for idx, case in enumerate(cases, start=1):
            safe_name = self._slugify(case.name or f"case_{idx}")
            target_path = output_dir / f"{safe_name}_{variant_suffix}.c"
            current_code = case.code
            compile_success = False
            compile_log: Optional[str] = None
            final_path = target_path
            for attempt in range(self.max_repairs + 1):
                target_path.write_text(current_code, encoding="utf-8")
                verification = self.verification_agent.verify(target_path)
                compile_log = verification.log
                if verification.success:
                    compile_success = True
                    success_counter += 1
                    final_path = output_dir / f"case_{variant_suffix}_{success_counter}.c"
                    final_path.write_text(current_code, encoding="utf-8")
                    if final_path != target_path and target_path.exists():
                        target_path.unlink()
                    break
                if attempt >= self.max_repairs:
                    break
                current_code = self.generalization_agent.repair_case(
                    pattern,
                    variant,
                    current_code,
                    compile_log or "",
                )
            processed.append(
                {
                    "name": case.name,
                    "rationale": case.rationale,
                    "path": str(final_path.relative_to(commit_dir)),
                    "variant": variant,
                    "success": compile_success,
                    "compile_log": compile_log or "",
                }
            )
        return processed

    @staticmethod
    def _slugify(name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9]+", "_", slug)
        slug = slug.strip("_") or "case"
        return slug[:80]

    @staticmethod
    def _locate_stage1_examples(base_dir: Path) -> Tuple[Optional[Path], Optional[Path]]:
        buggy_path = None
        fixed_path = None
        if not base_dir.exists():
            return buggy_path, fixed_path
        for candidate in base_dir.glob("*.c"):
            text = candidate.read_text(encoding="utf-8")
            if "// CHECK-MESSAGES:" in text and buggy_path is None:
                buggy_path = candidate
            elif "// CHECK-MESSAGES:" not in text and fixed_path is None:
                fixed_path = candidate
            if buggy_path and fixed_path:
                break
        return buggy_path, fixed_path
