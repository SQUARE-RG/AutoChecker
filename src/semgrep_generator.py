import json
import os
from pathlib import Path
from typing import Any, List

from config import global_config as config
from entity.abstractProduct import AbstractCase
from entity.abstractProduct import AbstractRule
from entity.concreteProduct_Semgrep import Checker_Semgrep
from loguru import logger
from plateform.semgrep import load_run_report
from plateform.semgrep import run_semgrep_rule_tool


def normalize_repo_path(path_text: str) -> Path:
    path = Path(str(path_text or "")).expanduser()
    if path.exists():
        return path
    text = str(path)
    marker = "/code_check/"
    if marker in text:
        candidate = Path(__file__).resolve().parents[1] / text.split(marker, 1)[1]
        if candidate.exists():
            return candidate
    return path


class Semgrep_CheckerGenerator(object):
    def __init__(
        self,
        rule: AbstractRule,
        all_Test_Case_List: List[AbstractCase] = None,
        skipped_Test_Cases: List[AbstractCase] = None,
        rule_result_dir: str = "",
    ):
        self.RULE = rule
        self.all_Test_Case_List = all_Test_Case_List if all_Test_Case_List is not None else []
        self.skipped_Test_Cases = skipped_Test_Cases if skipped_Test_Cases is not None else []
        self.result_dir = rule_result_dir
        self.total_cost = 0.0
        self.sample_to_case_path: dict[str, str] = {}

    def get_total_cost(self):
        return self.total_cost

    def generate_checker(self):
        os.makedirs(self.result_dir, exist_ok=True)

        sample_folder = self._resolve_sample_folder()
        target_language = self._target_language(sample_folder)
        max_attempts = int(config.get("arguments", {}).get("max_round", 3) or 3)
        semgrep_bin = str(config.get("file_paths", {}).get("semgrep", "") or "")
        output_dir = str(Path(self.result_dir) / "semgrep_run")

        returncode, stdout, stderr = run_semgrep_rule_tool(
            sample_folder=str(sample_folder),
            requirement=self.RULE.get_rule_description(),
            target_language=target_language,
            output_dir=output_dir,
            requirement_title=self.RULE.get_rule_name(),
            max_attempts=max_attempts,
            semgrep_bin=semgrep_bin,
            pattern_ir=bool(config.get("arguments", {}).get("semgrep_pattern_ir", True)),
            repair_mode=bool(config.get("arguments", {}).get("semgrep_repair_mode", True)),
        )

        run_dir = Path(output_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "stdout.log").write_text(stdout or "", encoding="utf-8")
        (run_dir / "stderr.log").write_text(stderr or "", encoding="utf-8")

        if returncode != 0:
            logger.error(f"Semgrep generation failed for {self.RULE.get_rule_name()}: {returncode}")
            logger.error(stderr[-2000:] if stderr else stdout[-2000:])
            return None

        report = load_run_report(output_dir)
        final_rule = str(report.get("final_rule_yaml") or "")
        if not final_rule or not Path(final_rule).is_file():
            logger.error(f"Semgrep generation produced no final rule for {self.RULE.get_rule_name()}")
            return None

        rule_yaml = Path(final_rule).read_text(encoding="utf-8")
        checker = Checker_Semgrep(
            checker_code=rule_yaml,
            passed_cases=self._passed_cases_from_report(report),
            report=report,
        )
        self.RULE.add_checker(checker)
        self._write_final_checker(rule_yaml, report)
        return self.RULE.get_checkers()

    def _resolve_sample_folder(self) -> Path:
        explicit = normalize_repo_path(str(self.RULE.get_rule_test_path() or ""))
        if explicit and (explicit / "bad").is_dir() and (explicit / "good").is_dir():
            self._map_existing_sample_cases(explicit)
            return explicit.resolve()

        success_paths = [str(normalize_repo_path(path)) for path in getattr(self.RULE, "success_case_list", []) if str(path).strip()]
        failed_paths = [str(normalize_repo_path(path)) for path in getattr(self.RULE, "failed_case_list", []) if str(path).strip()]
        if success_paths or failed_paths:
            return self._materialize_sample_folder(success_paths, failed_paths)

        positive = [str(normalize_repo_path(case.get_case_path())) for case in self.all_Test_Case_List if case.get_flag()]
        negative = [str(normalize_repo_path(case.get_case_path())) for case in self.all_Test_Case_List if not case.get_flag()]
        if positive or negative:
            return self._materialize_sample_folder(positive, negative)

        raise ValueError("Semgrep generation requires a paired sample folder or explicit good/bad case lists")

    def _materialize_sample_folder(self, good_paths: list[str], bad_paths: list[str]) -> Path:
        sample_root = Path(self.result_dir) / "paired_samples"
        bad_dir = sample_root / "bad"
        good_dir = sample_root / "good"
        bad_dir.mkdir(parents=True, exist_ok=True)
        good_dir.mkdir(parents=True, exist_ok=True)

        max_count = max(len(good_paths), len(bad_paths))
        for index in range(max_count):
            if index < len(bad_paths):
                copied = self._copy_case(Path(bad_paths[index]), bad_dir / f"test{index + 1}")
                self.sample_to_case_path[str(copied.resolve())] = str(normalize_repo_path(bad_paths[index]).resolve())
            if index < len(good_paths):
                copied = self._copy_case(Path(good_paths[index]), good_dir / f"test{index + 1}")
                self.sample_to_case_path[str(copied.resolve())] = str(normalize_repo_path(good_paths[index]).resolve())
        return sample_root.resolve()

    def _copy_case(self, source: Path, target_without_suffix: Path) -> Path:
        source = normalize_repo_path(str(source)).resolve()
        suffix = source.suffix or ".c"
        target = target_without_suffix.with_suffix(suffix)
        target.write_text(source.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        return target

    def _map_existing_sample_cases(self, sample_root: Path) -> None:
        for side in ("bad", "good"):
            for path in (sample_root / side).iterdir():
                if path.is_file():
                    self.sample_to_case_path[str(path.resolve())] = str(path.resolve())

    def _target_language(self, sample_folder: Path) -> str:
        explicit = str(getattr(self.RULE, "target_language", "") or "").strip()
        if explicit:
            return explicit
        configured = str(config.get("arguments", {}).get("semgrep_target_language", "") or "").strip()
        if configured:
            return configured

        suffixes = {path.suffix.lower() for side in ("bad", "good") for path in (sample_folder / side).glob("*") if path.is_file()}
        if suffixes & {".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx"}:
            return "cpp"
        if suffixes & {".c", ".h"}:
            return "c"
        if suffixes & {".py"}:
            return "python"
        if suffixes & {".js", ".jsx"}:
            return "javascript"
        if suffixes & {".ts", ".tsx"}:
            return "typescript"
        if suffixes & {".go"}:
            return "go"
        if suffixes & {".java"}:
            return "java"
        if suffixes & {".rs"}:
            return "rust"
        return "cpp"

    def _passed_cases_from_report(self, report: dict[str, Any]) -> list[AbstractCase]:
        best_eval = report.get("best_eval") if isinstance(report.get("best_eval"), dict) else {}
        missed = {
            self.sample_to_case_path.get(str(Path(str(item.get("path") or "")).expanduser().resolve()), str(Path(str(item.get("path") or "")).expanduser().resolve()))
            for item in best_eval.get("missed_bad_examples", [])
            if isinstance(item, dict)
        }
        flagged = {
            self.sample_to_case_path.get(str(Path(str(item.get("path") or "")).expanduser().resolve()), str(Path(str(item.get("path") or "")).expanduser().resolve()))
            for item in best_eval.get("flagged_good_examples", [])
            if isinstance(item, dict)
        }

        passed: list[AbstractCase] = []
        for case in self.all_Test_Case_List:
            path = str(normalize_repo_path(case.get_case_path()).resolve())
            if (not case.get_flag()) and path not in missed:
                passed.append(case)
            elif case.get_flag() and path not in flagged:
                passed.append(case)
        return passed

    def _write_final_checker(self, rule_yaml: str, report: dict[str, Any]) -> None:
        final_dir = Path(self.result_dir) / "final_checker"
        final_dir.mkdir(parents=True, exist_ok=True)
        (final_dir / f"{self.RULE.get_rule_name()}.yml").write_text(rule_yaml, encoding="utf-8")
        (final_dir / "semgrep_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
