from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .io_utils import read_json, write_json, write_text
from .llm_client import create_llm_client, invoke_text
from .rule_extractor import parse_json_response


InvokeFunction = Callable[[str, str], str]
logger = logging.getLogger(__name__)

CHECKPOINT_SCHEMA_VERSION = 2

FEASIBILITY_SYSTEM_PROMPT = """你是静态分析测试可行性评估Agent。你只判断一条规则在指定语言和版本下能否进入当前的单文件checker测试生成流程，不生成代码。

严格按顺序判断：
1. 规则的真实违背是否必须依赖两个或更多源文件、翻译单元或项目级上下文。如果必须，返回requires_multiple_files。
2. 如果可以在一个独立源文件中表达，是否至少存在一种真实违反规则、同时能通过指定语言基础编译/语法检查的negative case。编译warning不算失败；只有编译器非零退出才算失败。如果所有真实违背都会被编译器直接拒绝，返回compile_error_only。
3. 只有存在真实、单文件且可通过基础编译的negative case时，返回supported。

不得通过隐藏定义、条件编译排除违背代码、只写注释描述另一文件、删除违背点等方式把不可支持规则判为supported。必须结合规则描述和原文示例判断。
只输出合法JSON：{"status":"supported|requires_multiple_files|compile_error_only","reason":"简洁且具体的判断依据"}。
"""

TEST_GENERATION_SYSTEM_PROMPT = """你是静态分析 checker 的测试用例生成 Agent。你根据一条规则的描述和原文示例生成可被指定语言工具处理的独立代码文件。

必须遵守：
1. negative case 必须违反规则，未来 checker 应当报警；positive case 必须遵守规则，未来 checker 不应报警。
2. 每个文件只测试一个主要场景，代码自包含，默认只使用语言标准库。
3. 所有 negative 和 positive 文件都必须语法正确；negative 表示违反待检测规则，不表示允许无关语法错误。
4. 使用指定的语言版本、文件名和 Java 类名。
5. 不要简单修改变量名制造重复用例；不同 intent 必须覆盖不同语法形式或边界。
6. negative代码必须在主要违背语句上自主写入且只写入一个CHECK-MESSAGES注释；positive代码禁止出现CHECK-MESSAGES。
7. 如果规则的负例必须依赖多个源文件，或无法在保留违背点时通过基础编译，返回unsupported，不得伪造可编译但不包含真实违背的代码。
8. 只输出合法 JSON，不要输出 Markdown 代码围栏或解释。
"""

TEST_REPAIR_SYSTEM_PROMPT = """你是代码修复 Agent。请根据编译器或语法检查器诊断，只修复当前测试文件的语法、类型、声明、文件名或类名问题。

必须遵守：
1. 保持原 polarity 和 intent，不得把 negative 修成 compliant，也不得把 positive 修成 violation。
2. 不改变主要测试场景，不引入非标准第三方依赖。
3. negative必须保留且只保留一个CHECK-MESSAGES，positive禁止出现CHECK-MESSAGES。
4. 如果无法在单文件且可编译的前提下保留违背语义，返回unsupported，不得修掉真正的违背点。
5. 返回完整的单个代码文件。
6. 只输出合法 JSON，格式为 {"code": "修复后的完整代码"}；无法支持时返回 {"status":"unsupported","reason":"原因"}。
"""


@dataclass(frozen=True)
class CaseRequest:
    case_id: str
    polarity: str
    filename: str
    class_name: str | None = None


@dataclass
class GeneratedCase:
    case_id: str
    polarity: str
    intent: str
    filename: str
    code_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationResult:
    success: bool
    diagnostic: str


@dataclass(frozen=True)
class FeasibilityResult:
    status: str
    reason: str

    @property
    def supported(self) -> bool:
        return self.status == "supported"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class LanguageValidator:
    def __init__(
        self,
        language: str,
        *,
        compiler: str | None = None,
        c_standard: str = "c11",
        cpp_standard: str = "c++17",
        timeout_seconds: int = 30,
    ) -> None:
        self.language = _normalize_language(language)
        self.c_standard = c_standard
        self.cpp_standard = cpp_standard
        self.timeout_seconds = timeout_seconds
        self.tool = self._resolve_tool(compiler)

    @property
    def extension(self) -> str:
        return {"c": ".c", "cpp": ".cpp", "python": ".py", "java": ".java"}[
            self.language
        ]

    @property
    def language_version(self) -> str:
        return {
            "c": self.c_standard,
            "cpp": self.cpp_standard,
            "python": f"Python {sys.version_info.major}.{sys.version_info.minor}",
            "java": "Java",
        }[self.language]

    def validate(self, path: Path) -> ValidationResult:
        with tempfile.TemporaryDirectory(prefix="autochecker-validate-") as temp_dir:
            temp_path = Path(temp_dir)
            env = os.environ.copy()
            if self.language == "c":
                command = [self.tool, f"-std={self.c_standard}", "-fsyntax-only", str(path)]
            elif self.language == "cpp":
                command = [
                    self.tool,
                    f"-std={self.cpp_standard}",
                    "-fsyntax-only",
                    str(path),
                ]
            elif self.language == "python":
                env["PYTHONPYCACHEPREFIX"] = str(temp_path / "pycache")
                command = [self.tool, "-m", "py_compile", str(path)]
            else:
                command = [
                    self.tool,
                    "-proc:none",
                    "-d",
                    str(temp_path / "classes"),
                    str(path),
                ]
                (temp_path / "classes").mkdir()
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    env=env,
                )
            except subprocess.TimeoutExpired as exc:
                return ValidationResult(False, f"validation timed out: {exc}")
            diagnostic = "\n".join(
                part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
            )
            return ValidationResult(completed.returncode == 0, diagnostic)

    def _resolve_tool(self, compiler: str | None) -> str:
        if self.language == "python":
            return sys.executable
        candidates = {
            "c": ["clang", "gcc"],
            "cpp": ["clang++", "g++"],
            "java": ["javac"],
        }[self.language]
        if compiler:
            candidates = [compiler]
        for candidate in candidates:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
            candidate_path = Path(candidate)
            if candidate_path.is_file() and os.access(candidate_path, os.X_OK):
                return str(candidate_path.resolve())
        raise RuntimeError(
            f"No validator found for {self.language}; tried: {', '.join(candidates)}"
        )


def generate_rule_tests(
    rules_path: Path,
    output_dir: Path,
    output_rules: Path,
    *,
    language: str,
    negative_count: int = 10,
    positive_count: int = 10,
    batch_size: int = 4,
    max_repair_attempts: int = 3,
    compiler: str | None = None,
    c_standard: str = "c11",
    cpp_standard: str = "c++17",
    validation_timeout: int = 30,
    llm_timeout: int = 300,
    llm_max_retries: int = 5,
    retry_base_delay: float = 2.0,
    retry_max_delay: float = 60.0,
    workers: int = 1,
    llm_concurrency: int = 1,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    force: bool = False,
    invoke: InvokeFunction | None = None,
) -> dict[str, Any]:
    _validate_counts(negative_count, positive_count, batch_size, max_repair_attempts)
    if llm_timeout < 1:
        raise ValueError("llm_timeout must be positive")
    if llm_max_retries < 1:
        raise ValueError("llm_max_retries must be positive")
    if retry_base_delay < 0 or retry_max_delay < 0:
        raise ValueError("retry delays cannot be negative")
    if retry_base_delay > retry_max_delay:
        raise ValueError("retry_base_delay cannot exceed retry_max_delay")
    if workers < 1:
        raise ValueError("workers must be positive")
    if llm_concurrency < 1:
        raise ValueError("llm_concurrency must be positive")
    language = _normalize_language(language)
    rules_path = rules_path.resolve()
    output_dir = output_dir.resolve()
    output_rules = output_rules.resolve()
    if output_rules == rules_path:
        raise ValueError("output_rules must not overwrite the Stage-2 rules file")
    payload = read_json(rules_path)
    categories = payload.get("data")
    if not isinstance(categories, dict):
        raise ValueError("Rules JSON must contain an object field 'data'")

    validator = LanguageValidator(
        language,
        compiler=compiler,
        c_standard=c_standard,
        cpp_standard=cpp_standard,
        timeout_seconds=validation_timeout,
    )
    supplied_invoke = invoke
    thread_local = threading.local()
    llm_slots = threading.BoundedSemaphore(llm_concurrency)

    def raw_invoke(prompt: str, system: str) -> str:
        if supplied_invoke is not None:
            return supplied_invoke(prompt, system)
        client = getattr(thread_local, "client", None)
        if client is None:
            client = create_llm_client(
                model=model,
                api_key=api_key,
                base_url=base_url,
                timeout_seconds=llm_timeout,
                max_retries=0,
            )
            thread_local.client = client
        return invoke_text(client, prompt, system)

    def limited_invoke(prompt: str, system: str) -> str:
        logger.debug("llm_slot_wait")
        with llm_slots:
            logger.debug("llm_slot_acquired")
            return raw_invoke(prompt, system)

    updated = deepcopy(payload)
    report_path = output_dir / "generation_report.json"
    jobs: list[tuple[int, str, int, int, dict[str, Any], dict[str, Any]]] = []
    seen_titles: set[str] = set()
    for category, rules in updated["data"].items():
        if not isinstance(rules, list):
            raise ValueError(f"Category {category!r} must contain a rule array")
        for index, rule in enumerate(rules, start=1):
            main_title = str(rule.get("main_title") or "").strip()
            if not main_title:
                raise ValueError(f"Rule {index} in category {category!r} has no main_title")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", main_title):
                raise ValueError(f"Unsafe or invalid main_title: {main_title!r}")
            if main_title in seen_titles:
                raise ValueError(f"Duplicate main_title across categories: {main_title!r}")
            seen_titles.add(main_title)
            jobs.append((len(jobs), category, index, len(rules), deepcopy(rule), rule))

    report_slots: list[dict[str, Any] | None] = [None] * len(jobs)
    report_document: dict[str, Any] = {
        "schema_version": 1,
        "language": language,
        "status": "running",
        "workers": workers,
        "llm_concurrency": llm_concurrency,
        "rules": [],
        "completed_rule_count": 0,
        "failed_rule_count": 0,
    }
    write_json(output_rules, updated)
    write_json(report_path, report_document)
    completed_count = 0
    failed_count = 0

    def process_job(
        job: tuple[int, str, int, int, dict[str, Any], dict[str, Any]]
    ) -> tuple[int, dict[str, Any]]:
        job_index, category, index, category_size, rule, _target_rule = job
        main_title = str(rule["main_title"])
        logger.info(
            "rule_start category=%s index=%d/%d rule_id=%s main_title=%s",
            category,
            index,
            category_size,
            rule.get("rule_id"),
            main_title,
        )
        started_at = time.monotonic()
        try:
            result = _generate_for_rule(
                rule,
                category,
                output_dir,
                validator,
                limited_invoke,
                negative_count=negative_count,
                positive_count=positive_count,
                batch_size=batch_size,
                max_repair_attempts=max_repair_attempts,
                force=force,
                llm_max_retries=llm_max_retries,
                retry_base_delay=retry_base_delay,
                retry_max_delay=retry_max_delay,
            )
        except Exception as exc:
            logger.error(
                "rule_failed category=%s index=%d/%d main_title=%s error_type=%s error=%s; continuing",
                category,
                index,
                category_size,
                main_title,
                type(exc).__name__,
                exc,
            )
            logger.debug("rule failure traceback", exc_info=True)
            result = {
                "success": False,
                "rule_test_path": "",
                "negative_case_amount": 0,
                "positive_case_amount": 0,
                "generation_rounds": 0,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "unsupported_reasons": [],
            }
        elapsed = round(time.monotonic() - started_at, 3)
        return job_index, {
            "category": category,
            "rule_id": rule.get("rule_id"),
            "main_title": main_title,
            "elapsed_seconds": elapsed,
            **result,
        }

    def save_result(job_index: int, report: dict[str, Any]) -> None:
        nonlocal completed_count, failed_count
        target_rule = jobs[job_index][5]
        main_title = report["main_title"]
        report_slots[job_index] = report
        if report["success"]:
            target_rule["rule_test_path"] = report["rule_test_path"]
            target_rule["negative_case_amount"] = report["negative_case_amount"]
            target_rule["positive_case_amount"] = report["positive_case_amount"]
            completed_count += 1
            logger.info(
                "rule_complete main_title=%s negative=%d positive=%d rounds=%d elapsed=%.3fs",
                main_title,
                report["negative_case_amount"],
                report["positive_case_amount"],
                report["generation_rounds"],
                report["elapsed_seconds"],
            )
        else:
            target_rule["rule_test_path"] = ""
            target_rule.pop("negative_case_amount", None)
            target_rule.pop("positive_case_amount", None)
            failed_count += 1
        report_document["rules"] = [item for item in report_slots if item is not None]
        report_document["completed_rule_count"] = completed_count
        report_document["failed_rule_count"] = failed_count
        write_json(output_rules, updated)
        write_json(report_path, report_document)
        logger.info(
            "progress_saved completed_rules=%d failed_rules=%d output_rules=%s report=%s",
            completed_count,
            failed_count,
            output_rules,
            report_path,
        )

    if workers == 1:
        for job in jobs:
            save_result(*process_job(job))
    else:
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="rule-worker") as pool:
            futures = [pool.submit(process_job, job) for job in jobs]
            for future in as_completed(futures):
                save_result(*future.result())

    report_document["status"] = "completed"
    write_json(output_rules, updated)
    write_json(report_path, report_document)
    return {
        "language": language,
        "completed_rule_count": completed_count,
        "failed_rule_count": failed_count,
        "workers": workers,
        "llm_concurrency": llm_concurrency,
        "output_rules": str(output_rules),
        "report": str(report_path),
    }


def _generate_for_rule(
    rule: dict[str, Any],
    category: str,
    output_dir: Path,
    validator: LanguageValidator,
    invoke: InvokeFunction,
    *,
    negative_count: int,
    positive_count: int,
    batch_size: int,
    max_repair_attempts: int,
    force: bool,
    llm_max_retries: int,
    retry_base_delay: float,
    retry_max_delay: float,
) -> dict[str, Any]:
    main_title = str(rule["main_title"])
    rule_dir = output_dir / main_title
    staging_dir = output_dir / ".staging" / main_title
    checkpoint_path = output_dir / ".checkpoints" / f"{main_title}.json"
    input_hash = _rule_input_hash(
        rule,
        category,
        validator,
        negative_count=negative_count,
        positive_count=positive_count,
    )
    completed: dict[str, GeneratedCase] = {}
    feasibility: FeasibilityResult | None = None
    if checkpoint_path.exists() and not force:
        checkpoint = read_json(checkpoint_path)
        if (
            checkpoint.get("schema_version") == CHECKPOINT_SCHEMA_VERSION
            and checkpoint.get("input_hash") == input_hash
        ):
            feasibility_payload = checkpoint.get("feasibility")
            if isinstance(feasibility_payload, dict):
                feasibility = _parse_feasibility(feasibility_payload)
            for item in checkpoint.get("cases", []):
                case = GeneratedCase(**item)
                path = rule_dir / case.filename
                marker_validation = _validate_check_messages(
                    path.read_text(encoding="utf-8") if path.exists() else "",
                    case.polarity,
                    _checker_name(category, rule),
                )
                if (
                    path.exists()
                    and marker_validation.success
                    and validator.validate(path).success
                ):
                    completed[case.case_id] = case

    if feasibility is None:
        logger.info(
            "feasibility_start main_title=%s language=%s version=%s",
            main_title,
            validator.language,
            validator.language_version,
        )
        feasibility = _assess_rule_feasibility(
            rule,
            validator,
            invoke,
            llm_max_retries=llm_max_retries,
            retry_base_delay=retry_base_delay,
            retry_max_delay=retry_max_delay,
        )
        _write_checkpoint(
            checkpoint_path,
            input_hash,
            validator.language,
            completed,
            feasibility,
        )
        logger.info(
            "feasibility_complete main_title=%s status=%s reason=%s",
            main_title,
            feasibility.status,
            feasibility.reason,
        )
    else:
        logger.info(
            "feasibility_loaded main_title=%s status=%s reason=%s",
            main_title,
            feasibility.status,
            feasibility.reason,
        )

    if not feasibility.supported:
        error_type = {
            "requires_multiple_files": "unsupported_single_file",
            "compile_error_only": "compile_valid_negative_not_possible",
        }[feasibility.status]
        logger.warning(
            "rule_unsupported main_title=%s error_type=%s reason=%s",
            main_title,
            error_type,
            feasibility.reason,
        )
        return {
            "success": False,
            "rule_test_path": "",
            "negative_case_amount": 0,
            "positive_case_amount": 0,
            "generation_rounds": 0,
            "feasibility_status": feasibility.status,
            "feasibility_reason": feasibility.reason,
            "error_type": error_type,
            "error": feasibility.reason,
            "unsupported_reasons": [feasibility.reason],
        }

    logger.info(
        "checkpoint_loaded main_title=%s completed_cases=%d target_cases=%d",
        main_title,
        len(completed),
        negative_count + positive_count,
    )

    requests = _build_case_requests(
        negative_count, positive_count, validator.extension, validator.language
    )
    requests_by_id = {request.case_id: request for request in requests}
    seen_code = {case.code_hash for case in completed.values()}
    rejected_intents: list[str] = []
    expected_batches = math.ceil(len(requests) / batch_size)
    max_rounds = max(3, expected_batches * 3)
    rounds = 0
    last_error = ""
    unsupported_reasons: list[str] = []

    while len(completed) < len(requests) and rounds < max_rounds:
        missing = [request for request in requests if request.case_id not in completed]
        batch = _select_balanced_batch(missing, batch_size)
        rounds += 1
        logger.info(
            "batch_start main_title=%s round=%d/%d cases=%s",
            main_title,
            rounds,
            max_rounds,
            ",".join(item.case_id for item in batch),
        )
        prompt = _build_generation_prompt(
            rule,
            category,
            validator,
            batch,
            existing_intents=[case.intent for case in completed.values()] + rejected_intents,
        )
        response, _ = _invoke_json(
            invoke,
            prompt,
            TEST_GENERATION_SYSTEM_PROMPT,
            retries=llm_max_retries,
            retry_base_delay=retry_base_delay,
            retry_max_delay=retry_max_delay,
            phase=f"generation:{main_title}:round-{rounds}",
        )
        returned = response.get("cases", [])
        if not isinstance(returned, list):
            last_error = "Agent response field 'cases' is not an array"
            continue
        batch_by_id = {request.case_id: request for request in batch}
        made_progress = False
        for item in returned:
            if not isinstance(item, dict):
                continue
            case_id = str(item.get("case_id") or "")
            request = batch_by_id.get(case_id)
            if request is None or case_id in completed:
                continue
            if str(item.get("status") or "").lower() == "unsupported":
                reason = _clean_text(item.get("reason")) or "single-file case unsupported"
                unsupported_reasons.append(f"{case_id}: {reason}")
                rejected_intents.append(reason)
                last_error = unsupported_reasons[-1]
                logger.warning(
                    "case_unsupported main_title=%s case_id=%s reason=%s",
                    main_title,
                    case_id,
                    reason,
                )
                continue
            code = str(item.get("code") or "").strip()
            intent = _clean_text(item.get("intent"))
            if not code or not intent:
                continue
            result = _validate_and_repair(
                rule,
                request,
                intent,
                code,
                staging_dir,
                validator,
                invoke,
                category=category,
                max_repair_attempts=max_repair_attempts,
                llm_max_retries=llm_max_retries,
                retry_base_delay=retry_base_delay,
                retry_max_delay=retry_max_delay,
            )
            if result is None:
                rejected_intents.append(intent)
                last_error = f"{case_id} failed validation after repairs"
                continue
            repaired_code, final_intent = result
            code_hash = _normalized_code_hash(repaired_code, validator.language)
            if code_hash in seen_code:
                rejected_intents.append(final_intent)
                last_error = f"{case_id} duplicates an existing case"
                continue
            staging_path = staging_dir / request.filename
            final_path = rule_dir / request.filename
            write_text(staging_path, repaired_code.rstrip() + "\n")
            rule_dir.mkdir(parents=True, exist_ok=True)
            staging_path.replace(final_path)
            case = GeneratedCase(
                case_id=case_id,
                polarity=request.polarity,
                intent=final_intent,
                filename=request.filename,
                code_hash=code_hash,
            )
            completed[case_id] = case
            seen_code.add(code_hash)
            made_progress = True
            _write_checkpoint(
                checkpoint_path,
                input_hash,
                validator.language,
                completed,
                feasibility,
            )
            logger.info(
                "case_saved main_title=%s case_id=%s file=%s completed=%d/%d",
                main_title,
                case_id,
                final_path,
                len(completed),
                len(requests),
            )
        if not made_progress and not last_error:
            last_error = "Agent did not return any requested valid cases"

    negative_actual = sum(case.polarity == "negative" for case in completed.values())
    positive_actual = sum(case.polarity == "positive" for case in completed.values())
    success = negative_actual == negative_count and positive_actual == positive_count
    if success:
        _write_checkpoint(
            checkpoint_path,
            input_hash,
            validator.language,
            completed,
            feasibility,
        )
    else:
        missing_ids = sorted(set(requests_by_id) - set(completed))
        last_error = last_error or f"missing cases: {missing_ids}"
    return {
        "success": success,
        "rule_test_path": str(rule_dir.resolve()) if success else "",
        "negative_case_amount": negative_actual,
        "positive_case_amount": positive_actual,
        "generation_rounds": rounds,
        "feasibility_status": feasibility.status,
        "feasibility_reason": feasibility.reason,
        "error_type": "" if success else (
            "unsupported_single_file" if unsupported_reasons else "case_generation_failed"
        ),
        "error": "" if success else last_error,
        "unsupported_reasons": unsupported_reasons,
    }


def _validate_and_repair(
    rule: dict[str, Any],
    request: CaseRequest,
    intent: str,
    code: str,
    staging_dir: Path,
    validator: LanguageValidator,
    invoke: InvokeFunction,
    *,
    category: str,
    max_repair_attempts: int,
    llm_max_retries: int,
    retry_base_delay: float,
    retry_max_delay: float,
) -> tuple[str, str] | None:
    staging_path = staging_dir / request.filename
    current_code = code
    expected_check_name = _checker_name(category, rule)
    for attempt in range(max_repair_attempts + 1):
        write_text(staging_path, current_code.rstrip() + "\n")
        marker_validation = _validate_check_messages(
            current_code, request.polarity, expected_check_name
        )
        validation = marker_validation
        if marker_validation.success:
            validation = validator.validate(staging_path)
        if validation.success:
            return current_code, intent
        logger.warning(
            "validation_failed main_title=%s case_id=%s file=%s validator=%s repair_attempt=%d/%d diagnostic=%s",
            rule.get("main_title"),
            request.case_id,
            staging_path,
            validator.tool,
            attempt,
            max_repair_attempts,
            _single_line(validation.diagnostic, 600),
        )
        if attempt >= max_repair_attempts:
            return None
        prompt = _build_repair_prompt(
            rule, request, intent, current_code, validation.diagnostic, validator
        )
        logger.info(
            "repair_start main_title=%s case_id=%s attempt=%d/%d",
            rule.get("main_title"),
            request.case_id,
            attempt + 1,
            max_repair_attempts,
        )
        payload, _ = _invoke_json(
            invoke,
            prompt,
            TEST_REPAIR_SYSTEM_PROMPT,
            retries=llm_max_retries,
            retry_base_delay=retry_base_delay,
            retry_max_delay=retry_max_delay,
            phase=f"repair:{rule.get('main_title')}:{request.case_id}:{attempt + 1}",
        )
        if str(payload.get("status") or "").lower() == "unsupported":
            logger.warning(
                "repair_unsupported main_title=%s case_id=%s reason=%s",
                rule.get("main_title"),
                request.case_id,
                _clean_text(payload.get("reason")),
            )
            return None
        repaired = str(payload.get("code") or "").strip()
        if not repaired:
            return None
        current_code = repaired
    return None


def _build_generation_prompt(
    rule: dict[str, Any],
    category: str,
    validator: LanguageValidator,
    requests: list[CaseRequest],
    *,
    existing_intents: list[str],
) -> str:
    requested = [asdict(request) for request in requests]
    rule_input = {
        "main_title": rule.get("main_title"),
        "description": rule.get("description"),
        "rule_type": rule.get("rule_type"),
        "examples": rule.get("examples", []),
    }
    check_name = _checker_name(category, rule)
    comment_prefix = "#" if validator.language == "python" else "//"
    return f"""为下面这条规则生成指定的测试用例。

规则：
{json.dumps(rule_input, ensure_ascii=False, indent=2)}

目标语言：{validator.language}
语言版本：{validator.language_version}

必须生成且只能生成以下 case_id：
{json.dumps(requested, ensure_ascii=False, indent=2)}

已经使用或已失败的覆盖点，请不要重复：
{json.dumps(existing_intents, ensure_ascii=False, indent=2)}

CHECK-MESSAGES要求：
- negative代码必须自主标记唯一的主要违背行，且整个文件只能出现一次CHECK-MESSAGES；推荐同行格式：
  {comment_prefix} CHECK-MESSAGES: :[[@LINE]]:{{{{[0-9]+}}}}: warning: {{{{.*}}}} [{check_name}]
- 如果注释放在违背语句下一行，使用[[@LINE-1]]。
- positive代码中禁止出现CHECK-MESSAGES。
- 如果某个负例必须依赖多个源文件，或者无法在保留真实违背点的同时通过基础编译，返回status=unsupported和reason，不要返回伪造代码。

输出格式：
{{
  "cases": [
    {{
      "case_id": "必须与请求完全一致",
      "intent": "该文件覆盖的单一场景",
      "code": "完整代码，不使用 Markdown 围栏"
    }},
    {{
      "case_id": "无法单文件表达时对应的case_id",
      "status": "unsupported",
      "reason": "需要多文件或无法生成可编译负例的原因"
    }}
  ]
}}
"""


def _assess_rule_feasibility(
    rule: dict[str, Any],
    validator: LanguageValidator,
    invoke: InvokeFunction,
    *,
    llm_max_retries: int,
    retry_base_delay: float,
    retry_max_delay: float,
) -> FeasibilityResult:
    rule_input = {
        "rule_id": rule.get("rule_id"),
        "main_title": rule.get("main_title"),
        "description": rule.get("description"),
        "rule_type": rule.get("rule_type"),
        "examples": rule.get("examples", []),
        "target_language": validator.language,
        "language_version": validator.language_version,
        "validation": "single independent source file; syntax/compile check must exit 0",
    }
    prompt = "判断下面规则的测试可行性：\n" + json.dumps(
        rule_input, ensure_ascii=False, indent=2
    )
    payload, _ = _invoke_json(
        invoke,
        prompt,
        FEASIBILITY_SYSTEM_PROMPT,
        retries=llm_max_retries,
        retry_base_delay=retry_base_delay,
        retry_max_delay=retry_max_delay,
        phase=f"feasibility:{rule.get('main_title')}",
    )
    return _parse_feasibility(payload)


def _parse_feasibility(payload: dict[str, Any]) -> FeasibilityResult:
    allowed = {"supported", "requires_multiple_files", "compile_error_only"}
    status = _clean_text(payload.get("status")).lower()
    reason = _clean_text(payload.get("reason"))
    if status not in allowed:
        raise ValueError(
            "Feasibility response status must be one of: " + ", ".join(sorted(allowed))
        )
    if not reason:
        raise ValueError("Feasibility response must contain a non-empty reason")
    return FeasibilityResult(status=status, reason=reason)


def _build_repair_prompt(
    rule: dict[str, Any],
    request: CaseRequest,
    intent: str,
    code: str,
    diagnostic: str,
    validator: LanguageValidator,
) -> str:
    context = {
        "description": rule.get("description"),
        "rule_type": rule.get("rule_type"),
        "examples": rule.get("examples", []),
        "case": asdict(request),
        "intent": intent,
        "language": validator.language,
        "language_version": validator.language_version,
        "code": code,
        "diagnostic": diagnostic,
    }
    return "修复下面的单个测试文件：\n" + json.dumps(
        context, ensure_ascii=False, indent=2
    )


def _invoke_json(
    invoke: InvokeFunction,
    prompt: str,
    system_prompt: str,
    retries: int = 3,
    retry_base_delay: float = 2.0,
    retry_max_delay: float = 60.0,
    phase: str = "llm",
) -> tuple[dict[str, Any], str]:
    if retries < 1:
        raise ValueError("LLM retries must be positive")
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        started_at = time.monotonic()
        try:
            logger.info("llm_start phase=%s attempt=%d/%d", phase, attempt, retries)
            raw = invoke(prompt, system_prompt)
        except Exception as exc:
            last_error = exc
            retryable = _is_retryable_llm_error(exc)
            error_kind = type(exc).__name__
        else:
            try:
                parsed = parse_json_response(raw)
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                retryable = True
                error_kind = "invalid_json"
            else:
                logger.info(
                    "llm_complete phase=%s attempt=%d/%d elapsed=%.3fs",
                    phase,
                    attempt,
                    retries,
                    time.monotonic() - started_at,
                )
                return parsed, raw
        if not retryable or attempt >= retries:
            logger.error(
                "llm_failed phase=%s attempt=%d/%d error_type=%s error=%s",
                phase,
                attempt,
                retries,
                error_kind,
                last_error,
            )
            break
        delay = min(retry_max_delay, retry_base_delay * (2 ** (attempt - 1)))
        delay += random.uniform(0, min(1.0, delay * 0.2))
        logger.warning(
            "llm_retry phase=%s attempt=%d/%d error_type=%s error=%s next_delay=%.2fs",
            phase,
            attempt,
            retries,
            error_kind,
            last_error,
            delay,
        )
        time.sleep(delay)
    raise RuntimeError(f"LLM request failed after {retries} attempts: {last_error}") from last_error


def _build_case_requests(
    negative_count: int,
    positive_count: int,
    extension: str,
    language: str,
) -> list[CaseRequest]:
    requests: list[CaseRequest] = []
    for polarity, count in (("negative", negative_count), ("positive", positive_count)):
        for index in range(1, count + 1):
            case_id = f"{polarity}_{index:02d}"
            if language == "java":
                class_name = f"{polarity.title()}{index:02d}"
                filename = f"{class_name}{extension}"
            else:
                class_name = None
                filename = f"{case_id}{extension}"
            requests.append(CaseRequest(case_id, polarity, filename, class_name))
    return requests


def _select_balanced_batch(
    missing: list[CaseRequest], batch_size: int
) -> list[CaseRequest]:
    by_polarity = {
        "negative": [item for item in missing if item.polarity == "negative"],
        "positive": [item for item in missing if item.polarity == "positive"],
    }
    selected: list[CaseRequest] = []
    while len(selected) < batch_size and any(by_polarity.values()):
        for polarity in ("negative", "positive"):
            if by_polarity[polarity] and len(selected) < batch_size:
                selected.append(by_polarity[polarity].pop(0))
    return selected


def _write_checkpoint(
    path: Path,
    input_hash: str,
    language: str,
    completed: dict[str, GeneratedCase],
    feasibility: FeasibilityResult,
) -> None:
    write_json(
        path,
        {
            "schema_version": CHECKPOINT_SCHEMA_VERSION,
            "input_hash": input_hash,
            "language": language,
            "feasibility": feasibility.to_dict(),
            "cases": [completed[key].to_dict() for key in sorted(completed)],
        },
    )


def _rule_input_hash(
    rule: dict[str, Any],
    category: str,
    validator: LanguageValidator,
    *,
    negative_count: int,
    positive_count: int,
) -> str:
    relevant = {
        "main_title": rule.get("main_title"),
        "description": rule.get("description"),
        "rule_type": rule.get("rule_type"),
        "examples": rule.get("examples", []),
        "language": validator.language,
        "language_version": validator.language_version,
        "negative_count": negative_count,
        "positive_count": positive_count,
        "check_messages_contract": 1,
        "check_name": _checker_name(category, rule),
    }
    encoded = json.dumps(relevant, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_code_hash(code: str, language: str) -> str:
    if language in {"c", "cpp", "java"}:
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        code = re.sub(r"//[^\n]*", "", code)
    elif language == "python":
        code = re.sub(r"(?m)^\s*#.*$", "", code)
    normalized = re.sub(r"\s+", "", code)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalize_language(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {"c++": "cpp", "py": "python"}
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"c", "cpp", "python", "java"}:
        raise ValueError("language must be one of: c, cpp, python, java")
    return normalized


def _validate_counts(
    negative_count: int,
    positive_count: int,
    batch_size: int,
    max_repair_attempts: int,
) -> None:
    if negative_count < 0 or positive_count < 0:
        raise ValueError("case counts cannot be negative")
    if negative_count + positive_count == 0:
        raise ValueError("at least one test case must be requested")
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    if max_repair_attempts < 0:
        raise ValueError("max_repair_attempts cannot be negative")


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _checker_name(category: str, rule: dict[str, Any]) -> str:
    rule_part = str(rule.get("rule_id") or rule.get("main_title") or "rule").lower()
    raw = f"{category}-{rule_part}".lower()
    return re.sub(r"[^a-z0-9-]+", "-", raw).strip("-")


def _validate_check_messages(
    code: str, polarity: str, expected_check_name: str
) -> ValidationResult:
    marker_count = code.count("CHECK-MESSAGES")
    if polarity == "positive":
        if marker_count:
            return ValidationResult(False, "positive case must not contain CHECK-MESSAGES")
        return ValidationResult(True, "")
    if marker_count != 1:
        return ValidationResult(
            False,
            f"negative case must contain exactly one CHECK-MESSAGES; found {marker_count}",
        )
    if f"[{expected_check_name}]" not in code:
        return ValidationResult(
            False,
            f"CHECK-MESSAGES must contain checker name [{expected_check_name}]",
        )
    return ValidationResult(True, "")


def _is_retryable_llm_error(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    status_code = getattr(exc, "status_code", None) or getattr(
        response, "status_code", None
    )
    if status_code is not None:
        return status_code == 429 or status_code >= 500
    name = type(exc).__name__.lower()
    return isinstance(exc, (TimeoutError, ConnectionError)) or any(
        token in name
        for token in ("timeout", "connection", "ratelimit", "internalserver")
    )


def _single_line(value: str, limit: int) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip()
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 3] + "..."
