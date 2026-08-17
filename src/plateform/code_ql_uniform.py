"""语言无关的 CodeQL 平台操作。

database 创建、qlpack.yml 生成、编译、运行查询 ——
所有语言相关参数从 LanguageConfig 获取。
"""

import os
import subprocess
from typing import List, Tuple

from loguru import logger

from codeql_language_config import LanguageConfig
from config import global_config

# .ql 查询模板路径
_QL_TEMPLATE_DIR = "/root/code_check/src/prompt/codeql_prompt/prompt_txt"
_QL_TEMPLATES = {
    "cpp": os.path.join(_QL_TEMPLATE_DIR, "standard.ql"),
    "python": os.path.join(_QL_TEMPLATE_DIR, "standard_python.ql"),
}


# ── qlpack ────────────────────────────────────────────────

def write_qlpack(rule_name: str, output_dir: str, lang_config: LanguageConfig,
                 extra_dependencies: List[str] = None) -> str:
    """在 output_dir 下按语言生成 qlpack.yml，返回写入路径。

    依赖来源（单一权威）：
    - 基础依赖：lang_config.qlpack_dependency（按语言区分，缺失直接报错）
    - 额外依赖：extra_dependencies（规则级可选，如 ["codeql/dataflow"]）
    """
    if not lang_config.qlpack_dependency:
        raise ValueError(
            f"语言 {lang_config.language} 未配置 qlpack 依赖，拒绝生成 qlpack.yml")

    deps = [lang_config.qlpack_dependency]
    for dep in (extra_dependencies or []):
        if dep not in deps:
            deps.append(dep)

    deps_yaml = "\n".join(f"  {dep}" for dep in deps)
    content = f"""name: autochecker-{rule_name}
version: 0.0.0
dependencies:
{deps_yaml}
"""
    path = os.path.join(output_dir, "qlpack.yml")
    os.makedirs(output_dir, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    logger.info(f"qlpack.yml written → {path}")
    return path


# ── CodeQL database ───────────────────────────────────────

def _codeql_database_name(case_path: str) -> str:
    case_dir, case_file = os.path.split(case_path)
    case_name, _ = os.path.splitext(case_file)
    return os.path.join(case_dir, case_name + "_db")


def create_database(case_path: str, lang_config: LanguageConfig) -> str | None:
    """为单个测试用例创建 CodeQL database。

    解释型语言（无 database_build_command，如 Python）：
      extractor 会扫描整个 --source-root——必须把单个用例复制到隔离目录，
      否则 database 会混入同目录下其他测试用例的代码（verify 结果失真）。
    编译型语言（有 --command）：extractor 跟随编译，只提取被编译的文件。
    """
    import shutil
    import tempfile

    database_path = _codeql_database_name(case_path)
    if os.path.exists(database_path):
        logger.info(f"Database already exists, skip: {database_path}")
        return database_path

    case_dir = os.path.dirname(case_path)
    cmd = [
        "codeql", "database", "create",
        database_path,
        f"--language={lang_config.codeql_language_flag}",
    ]

    isolated_dir = None
    if lang_config.database_build_command:
        cmd.append(f"--command={lang_config.database_build_command.format(case_path=case_path)}")
        cmd.append(f"--source-root={case_dir}")
    else:
        # 解释型语言：单用例隔离目录
        isolated_dir = tempfile.mkdtemp(prefix="codeql_case_iso_")
        isolated_case = os.path.join(isolated_dir, os.path.basename(case_path))
        shutil.copy(case_path, isolated_case)
        cmd.append(f"--source-root={isolated_dir}")
        logger.info(f"隔离目录: {isolated_dir}（只含 {os.path.basename(case_path)}）")

    logger.info(f"Creating database: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    finally:
        if isolated_dir:
            shutil.rmtree(isolated_dir, ignore_errors=True)

    if result.returncode == 0:
        logger.info(f"Database created: {database_path}")
        return database_path
    else:
        logger.error(f"Database creation failed: {database_path}\n{result.stderr}")
        return None


def create_databases_for_test_cases(cases, lang_config: LanguageConfig) -> List[str]:
    """批量创建 CodeQL database。"""
    db_paths = []
    for case in cases:
        db_path = create_database(case.get_case_path(), lang_config)
        if db_path:
            db_paths.append(db_path)
    return db_paths


def case_path_to_database_path(case_path: str) -> str | None:
    """从测试用例路径推导 database 路径并验证存在。"""
    db_path = _codeql_database_name(case_path)
    if not os.path.exists(db_path):
        logger.error(f"Database not found for: {case_path}")
        return None
    return db_path


# ── 编译 / 运行 ──────────────────────────────────────────

def compiler_code_ql(query_path: str) -> Tuple[int, str, str, bool]:
    """编译 CodeQL 查询（语言无关）。"""
    logger.info("---------------------- Compiling CodeQL ----------------------")
    result = subprocess.run(
        ["codeql", "query", "compile", query_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    success = result.returncode == 0
    if success:
        logger.info("CodeQL compilation succeeded")
    else:
        logger.info(f"CodeQL compilation failed:\n{result.stderr}")
    return result.returncode, result.stdout, result.stderr, success


def run_code_ql_with_query(query_path: str, database_path: str, output_path: str) -> Tuple[str, int]:
    """运行 CodeQL 查询并返回 (输出文本, warning 数量)。warnings=-1 表示运行失败。"""
    logger.info("---------------------- Running CodeQL ----------------------")
    cmd = [
        "codeql", "database", "analyze",
        database_path,
        "--format=csv",
        f"--output={output_path}",
        query_path,
        "--rerun",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        logger.error(f"Run failed on {database_path}, rc={proc.returncode}")
        return proc.stdout, -1

    with open(output_path, "r") as f:
        output_content = f.read()
    stripped = output_content.strip()
    warning_count = len(stripped.split("\n")) if stripped else 0
    logger.info(f"Run succeeded, warnings: {warning_count}")
    return proc.stdout, warning_count


# ── 查询模板 ──────────────────────────────────────────────

def pre_generate_query_template(checker_name: str, output_dir: str, lang_config: LanguageConfig) -> str:
    """生成 .ql 查询模板文件到 output_dir/{checker_name}.ql，返回写入路径。

    模板从 standard.ql 读取，替换 import 语句为语言对应的版本。
    """
    os.makedirs(output_dir, exist_ok=True)
    target_path = os.path.join(output_dir, f"{checker_name}.ql")

    template_path = _QL_TEMPLATES.get(
        lang_config.language,
        os.path.join(_QL_TEMPLATE_DIR, "standard.ql"),
    )
    with open(template_path, "r") as src:
        template_content = src.read()

    with open(target_path, "w") as dst:
        dst.write(template_content)

    logger.info(f"Query template generated → {target_path}")
    return target_path
