#!/usr/bin/env python3
"""Generate the manual-review workbook for AutoQL analysis runs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "doc" / "20026-11-02" / "autoql_analysis_failure_report.xlsx"
BATCH_DIR = ROOT / "autoql_runs" / "batch-20261104-042207"


FAILURE_REVIEWS = {
    "CVE-2025-30067": {
        "failure_type": "结构化输出解析失败",
        "stage": "AnalysisBrief 落盘前",
        "reason": "Explorer 在最终文本中输出了 fenced JSON，但 result.structured_response 为空；agent.py 第 143-145 行直接抛出 ValueError。",
        "evidence": "日志包含完整 vulnerability_summary 和 E1-E6，随后报 Analysis explorer returned no structured response；未生成 vuln_spec.json。",
        "impact": "本次 analysis 被标记 infrastructure_error，后续阶段无法消费结果。",
        "suggestion": "检查 response_format/工具绑定；对最终文本中的合法 JSON 增加受 schema 校验的兜底解析。",
    },
    "CVE-2025-22227": {
        "failure_type": "结构化输出解析失败",
        "stage": "AnalysisBrief 落盘前",
        "reason": "Explorer 在 Markdown 代码块中返回完整 JSON，但框架只读取 structured_response，不解析消息正文。",
        "evidence": "日志包含 E1-E7，随后 structured_response 为 None 并抛出 ValueError；无 vuln_spec.json。",
        "impact": "分析内容丢失，流水线失败。",
        "suggestion": "强化结构化输出约束，并为合法 JSON 正文提供严格 schema 兜底。",
    },
    "CVE-2023-51982": {
        "failure_type": "结构化输出解析失败",
        "stage": "AnalysisBrief 落盘前",
        "reason": "Explorer 用 fenced JSON 返回 AnalysisBrief，未写入 structured_response。",
        "evidence": "日志中已有 E1-E5 和完整摘要，紧接 ValueError；无 vuln_spec.json。",
        "impact": "有效分析未转成正式产物。",
        "suggestion": "修正模型结构化响应配置；增加 schema 校验后的正文恢复机制。",
    },
    "CVE-2025-3910": {
        "failure_type": "结构化输出解析失败",
        "stage": "AnalysisBrief 落盘前",
        "reason": "Explorer 返回普通 JSON 文本而非 structured_response，框架未接受。",
        "evidence": "日志包含完整 E1-E6 JSON，随后报 Analysis explorer returned no structured response。",
        "impact": "没有 analysis_brief.json/vuln_spec.json，批处理记为失败。",
        "suggestion": "统一模型最终输出通道；将正文兜底解析限定为单个 JSON 对象并执行现有 validate_brief。",
    },
    "CVE-2023-51441": {
        "failure_type": "结构化输出解析失败",
        "stage": "AnalysisBrief 落盘前",
        "reason": "Explorer 返回单行 JSON 正文，但 structured_response 为空。",
        "evidence": "日志中已有 E1-E2，随后 agent.py 抛 ValueError；无 vuln_spec.json。",
        "impact": "分析结果未持久化。",
        "suggestion": "检查 provider 对 structured output 的支持，并加入严格 JSON/schema 兜底。",
    },
    "CVE-2025-2240": {
        "failure_type": "结构化输出解析失败",
        "stage": "AnalysisBrief 落盘前",
        "reason": "Explorer 将 JSON 包在 <AnalysisBrief> 标签中作为文本返回，框架只检查 structured_response。",
        "evidence": "日志含 E1-E8 和完整摘要，之后抛 ValueError；无 vuln_spec.json。",
        "impact": "analysis 阶段失败，结果不可被后续流程使用。",
        "suggestion": "从 system prompt 去掉旧标签式输出暗示；确保 schema 绑定生效，并增加受控兜底。",
    },
    "CVE-2022-32287": {
        "failure_type": "漏洞修复机制误判",
        "stage": "漏洞语义与证据审查",
        "reason": "E1/E3 正确定位 Zip Slip 和调用链，但 E2 的 fixed 代码仍直接 new File(targetDir, jarEntry.getName())；E4 仅做 DirFileFilter 分隔符替换，且该调用链中 filter 或 _dirPath 为 null，不能形成目录 containment。摘要却声称修复恢复了目录约束。",
        "evidence": "fixed FileUtil.java 755-786 仍无 normalize/canonical/startsWith(targetDir) 检查；commit 1088f615 只是 file-handling cleanup。",
        "impact": "vuln_spec 对根因判断部分正确，但修复机制和修复证据错误，不能用于生成可靠 Query。",
        "suggestion": "将该结果拒绝；先校正数据集 fixed commit/ground truth，再重新分析。若沿用当前 commit，应明确报告未观察到有效修复。",
    },
    "CVE-2024-48944": {
        "failure_type": "漏洞修复机制误判",
        "stage": "漏洞语义与证据审查",
        "reason": "摘要把 Base64 改为 AES 解释为不可伪造，但 fixed decodeHost 对以 http:// 开头的输入直接原样返回，解密失败也回退原 host；攻击者仍可直接提交任意 HTTP 目标。摘要自身也承认 fallback，却仍宣称恢复安全不变量。",
        "evidence": "fixed NBasicController.decodeHost：host.startsWith(\"http://\") 直接 return host；catch/空解密结果同样返回 host。",
        "impact": "修复有效性结论与代码不一致，spec 会引导 Query 关注加密而遗漏真正的目标主机约束。",
        "suggestion": "将结果判失败；确认数据集 commit 是否完整，并要求分析验证所有 bypass/fallback 分支。",
    },
    "CVE-2025-26795": {
        "failure_type": "跨 CVE 证据污染",
        "stage": "漏洞范围界定",
        "reason": "目标 CVE 仅描述 IoTDB JDBC driver 日志泄露，但摘要和证据同时纳入 OpenIdAuthorizer、User.toString 等属于同一共享修复 commit 的其他问题。",
        "evidence": "NVD 描述聚焦 iotdb-jdbc；当前 E3-E6 扩展到 OpenIdAuthorizer/User。CVE-2025-26864 与其使用相同 buggy/fix commit，数据集 fix_info 也重复收录多个文件。",
        "impact": "根因边界过宽，可能生成同时命中多个无关路径的 CodeQL Query。",
        "suggestion": "以 CVE metadata 约束分析范围；共享 commit 时只保留与当前组件/描述对应的证据。",
    },
    "CVE-2025-26864": {
        "failure_type": "跨 CVE 证据污染",
        "stage": "漏洞范围界定",
        "reason": "目标 CVE 聚焦 OpenIdAuthorizer，但摘要混入 JDBC DataSourceFactory 和 User.toString 路径；这是共享 commit 带来的范围扩张。",
        "evidence": "NVD 描述明确为 OpenIdAuthorizer；当前 E1-E2 是 JDBC driver，其他证据也超出目标组件。两个 IoTDB CVE 共用 34fcaff6 修复 commit。",
        "impact": "vuln_spec 不再代表单一 CVE，后续 Query 设计会混合不同 source/sink。",
        "suggestion": "结合 CVE description/CWE/组件名对 patch hunks 做归属；本 CVE 只保留 OpenIdAuthorizer 对应链路。",
    },
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_project_rows():
    with (ROOT / "autoql_data" / "project_info.csv").open(
        newline="", encoding="utf-8-sig"
    ) as stream:
        return {row["cve_id"]: row for row in csv.DictReader(stream)}


def selected_runs():
    runs = [
        ROOT / "autoql_runs" / "CVE-2022-25842-20261103-182319",
        ROOT / "autoql_runs" / "CVE-2022-32287-20261104-030731",
    ]
    runs.extend(sorted((BATCH_DIR / "runs").iterdir()))
    return runs


def collect_rows():
    projects = load_project_rows()
    summary = read_json(BATCH_DIR / "summary.json")
    batch_results = {item["cve"]: item for item in summary["results"]}
    rows = []
    for run_dir in selected_runs():
        manifest = read_json(run_dir / "manifest.json")
        result = read_json(run_dir / "result.json")
        cve = manifest["cve_id"]
        project = projects.get(cve, {})
        review = FAILURE_REVIEWS.get(cve)
        batch = batch_results.get(cve, {})
        spec_path = run_dir / "vuln_spec.json"
        spec = read_json(spec_path) if spec_path.exists() else None
        rows.append(
            {
                "CVE": cve,
                "CWE": project.get("cwe_id", ""),
                "CWE名称": project.get("cwe_name", ""),
                "项目": project.get("project_slug", ""),
                "运行目录": str(run_dir.relative_to(ROOT)),
                "流水线状态": result.get("final_status", batch.get("status", "")),
                "人工审查结论": "失败" if review else "未发现明显问题",
                "失败类型": review["failure_type"] if review else "",
                "失败阶段": review["stage"] if review else "",
                "失败原因": review["reason"] if review else "",
                "直接证据": review["evidence"] if review else "",
                "影响": review["impact"] if review else "",
                "建议": review["suggestion"] if review else "",
                "buggy commit": manifest.get("buggy_commit", ""),
                "fix commit": manifest.get("fix_commit", ""),
                "Evidence数量": len(spec.get("evidence", [])) if spec else 0,
                "耗时(秒)": batch.get("elapsed_seconds", ""),
            }
        )
    return rows


def style_table(ws, widths):
    header_fill = PatternFill("solid", fgColor="1F4E78")
    failed_fill = PatternFill("solid", fgColor="FCE4D6")
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        if any(cell.value == "失败" for cell in row):
            for cell in row:
                cell.fill = failed_fill
    for index, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.row_dimensions[1].height = 28


def add_rows_sheet(wb, title, rows):
    ws = wb.create_sheet(title)
    headers = list(rows[0])
    ws.append(headers)
    for index, row in enumerate(rows, 1):
        ws.append([index] + [row[key] for key in headers[1:]] if headers[0] == "序号" else [row[key] for key in headers])
    widths = [16, 12, 38, 32, 55, 20, 18, 22, 24, 70, 70, 55, 65, 44, 44, 14, 14]
    style_table(ws, widths[: len(headers)])
    return ws


def build_workbook(rows, output):
    wb = Workbook()
    wb.remove(wb.active)
    failures = [row for row in rows if row["人工审查结论"] == "失败"]
    add_rows_sheet(wb, "失败清单", failures)
    add_rows_sheet(wb, "全量审查", rows)

    ws = wb.create_sheet("统计与口径")
    counts = Counter(row["失败类型"] for row in failures)
    stats = [
        ("项目", "值"),
        ("审查运行数", len(rows)),
        ("失败 CVE 数", len(failures)),
        ("未发现明显问题数", len(rows) - len(failures)),
        ("结构化输出解析失败", counts["结构化输出解析失败"]),
        ("漏洞修复机制误判", counts["漏洞修复机制误判"]),
        ("跨 CVE 证据污染", counts["跨 CVE 证据污染"]),
        ("选取口径", "CVE-2022-25842 固定使用 autoql_runs/CVE-2022-25842-20261103-182319；CVE-2022-32287 使用独立运行；其余使用 batch-20261104-042207/runs。"),
        ("失败口径", "包括未生成 vuln_spec 的流水线失败，以及已生成 vuln_spec 但根因/修复/证据范围存在实质错误的语义失败。"),
        ("审查依据", "result.json、vuln_spec.json、manifest.json、运行日志、CVE/CWE metadata、buggy/fixed 源码及 commit diff。"),
        ("说明", "“未发现明显问题”表示本轮静态人工复核未识别出实质错误，不等同于形式化正确性证明。"),
    ]
    for row in stats:
        ws.append(row)
    style_table(ws, [28, 120])

    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)


def verify_workbook(output, expected_rows, expected_failures):
    workbook = load_workbook(output, read_only=True, data_only=True)
    assert workbook.sheetnames == ["失败清单", "全量审查", "统计与口径"]
    assert workbook["失败清单"].max_row - 1 == expected_failures
    assert workbook["全量审查"].max_row - 1 == expected_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows = collect_rows()
    build_workbook(rows, args.output)
    verify_workbook(args.output, len(rows), len(FAILURE_REVIEWS))
    print(f"wrote {args.output} ({len(rows)} runs, {len(FAILURE_REVIEWS)} failures)")


if __name__ == "__main__":
    main()
