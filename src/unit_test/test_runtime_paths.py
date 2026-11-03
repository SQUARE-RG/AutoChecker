from pathlib import Path

from help import runtime_paths
from plateform import clang_tidy


def test_runtime_temp_file_creates_configured_subdirectory(
    tmp_path: Path, monkeypatch
):
    configured_root = tmp_path / "runtime"
    monkeypatch.setitem(
        runtime_paths.global_config["checker"],
        "temp_test_dir",
        str(configured_root),
    )

    output = runtime_paths.runtime_temp_file("logs", "checker-test.log")

    assert output == configured_root / "logs" / "checker-test.log"
    assert output.parent.is_dir()


def test_clang_tidy_default_log_is_written_below_runtime_root(
    tmp_path: Path, monkeypatch
):
    configured_root = tmp_path / "runtime"
    monkeypatch.setitem(
        runtime_paths.global_config["checker"],
        "temp_test_dir",
        str(configured_root),
    )

    class Completed:
        returncode = 0
        stdout = "sample.cpp:1:1: warning: generated warning\n"

    monkeypatch.setattr(clang_tidy.subprocess, "run", lambda *args, **kwargs: Completed())

    _, warning_count = clang_tidy.run_Checker_with_Check_clang_tidy(
        test_case_path=str(tmp_path / "sample.cpp"),
        rule_name="ucassaat-sample-rule",
        temp_dir=str(configured_root / "sample"),
        include_dir=str(tmp_path),
    )

    log_path = configured_root / "logs" / "ucassaat-sample-rule-test.log"
    assert warning_count == 1
    assert log_path.read_text(encoding="utf-8") == Completed.stdout
