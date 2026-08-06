import argparse
import json
import os
import shutil
import time
from pathlib import Path

from config import global_config
from entity.factory import Factory_Semgrep
from loguru import logger
from semgrep_generator import Semgrep_CheckerGenerator


def init_logger(log_dir: str = "./logs", result_name: str = "semgrep"):
    os.makedirs(log_dir, exist_ok=True)
    time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    logger.add(
        f"{log_dir}/{result_name}-{time_stamp}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
    )


def normalize_repo_path(path_text: str) -> Path:
    path = Path(str(path_text or "")).expanduser()
    if path.exists():
        return path
    marker = "/code_check/"
    text = str(path)
    if marker in text:
        candidate = Path(__file__).resolve().parents[1] / text.split(marker, 1)[1]
        if candidate.exists():
            return candidate
    return path


def load_paired_cases(rule_test_path: str, rule_name: str):
    factory = Factory_Semgrep()
    cases = []
    root = normalize_repo_path(rule_test_path)
    for label, is_good in (("bad", False), ("good", True)):
        side_dir = root / label
        if not side_dir.is_dir():
            continue
        for path in sorted(side_dir.iterdir(), key=lambda item: item.name):
            if not path.is_file():
                continue
            case = factory.create_case()
            case.case_code = path.read_text(encoding="utf-8", errors="replace")
            case.case_description = f"Semgrep {label} case for {rule_name} in {path}"
            case.case_flag = is_good
            case.case_path = str(path.resolve())
            cases.append(case)
    return cases


def build_rule(rule_info: dict):
    rule = Factory_Semgrep().create_rule()
    rule.rule_name = str(rule_info["main_title"])
    rule.rule_description = str(rule_info.get("description", ""))
    rule.rule_test_path = str(normalize_repo_path(rule_info.get("rule_test_path", "")))
    rule.rule_category = str(rule_info.get("category", "semgrep"))
    rule.success_case_list = [str(normalize_repo_path(path)) for path in rule_info.get("success_case_list", [])]
    rule.failed_case_list = [str(normalize_repo_path(path)) for path in rule_info.get("failed_case_list", [])]
    rule.negative_case_amount = int(rule_info.get("negative_case_amount", 0) or 0)
    rule.positive_case_amount = int(rule_info.get("positive_case_amount", 0) or 0)
    rule.target_language = str(rule_info.get("target_language", "") or rule_info.get("language", "") or "")
    return rule


def run_rule(rule_info: dict, result_root: Path) -> dict:
    rule = build_rule(rule_info)
    cases = load_paired_cases(rule.rule_test_path, rule.rule_name)
    rule_result_dir = result_root / rule.rule_name
    if rule_result_dir.exists():
        shutil.rmtree(rule_result_dir)
    rule_result_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    generator = Semgrep_CheckerGenerator(rule, all_Test_Case_List=cases, rule_result_dir=str(rule_result_dir))
    checkers = generator.generate_checker()
    elapsed = time.perf_counter() - start

    updated = dict(rule_info)
    updated["time"] = f"{elapsed:.2f}"
    updated["total_cost"] = f"{generator.get_total_cost():.6f}"
    if checkers is None:
        updated["issuccess"] = "False"
        updated["performance"] = f"0/{len(cases)}"
        return updated

    final_checker = checkers[-1]
    passed = final_checker.get_passed_cases()
    passed_paths = [case.get_case_path() for case in passed]
    failed_paths = [case.get_case_path() for case in cases if case.get_case_path() not in passed_paths]
    report = final_checker.get_report()
    best_eval = report.get("best_eval", {}) if isinstance(report, dict) else {}

    updated["issuccess"] = "True"
    updated["performance"] = f"{len(passed_paths)}/{len(cases)}"
    updated["success_case_list"] = passed_paths
    updated["failed_case_list"] = failed_paths
    updated["semgrep_final_rule"] = report.get("final_rule_yaml", "") if isinstance(report, dict) else ""
    updated["semgrep_bad_hit"] = best_eval.get("bad_hit", 0)
    updated["semgrep_bad_total"] = best_eval.get("bad_total", 0)
    updated["semgrep_good_fp"] = best_eval.get("good_hit", 0)
    updated["semgrep_good_total"] = best_eval.get("good_total", 0)
    return updated


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Semgrep rules from AutoChecker rule JSON.")
    parser.add_argument("rules_json", nargs="?", default=global_config.get("arguments", {}).get("rules_json_path", ""))
    parser.add_argument("--result-dir", default=global_config.get("result", {}).get("result_dir", "./code_check/result-generation/"))
    return parser.parse_args()


def main():
    init_logger()
    args = parse_args()
    rules_json = args.rules_json or "./code_check/experiment/gjb8114/rule_codeql/jgb8114_single_rules.json"
    with open(rules_json, "r", encoding="utf-8") as handle:
        rule_data = json.load(handle)

    result_root = Path(args.result_dir) / "semgrep"
    result_root.mkdir(parents=True, exist_ok=True)
    for rule_package, rule_list in rule_data.get("data", {}).items():
        for index, rule_info in enumerate(rule_list):
            logger.info(f"Generating Semgrep rule: {rule_info.get('main_title')}")
            rule_list[index] = run_rule(rule_info, result_root)

    result_path = result_root / "checker_generation_result.json"
    result_path.write_text(json.dumps(rule_data, ensure_ascii=False, indent=4), encoding="utf-8")
    logger.info(f"Semgrep generation result saved to: {result_path}")


if __name__ == "__main__":
    main()
