"""CodeQL 多语言配置 — 所有语言差异集中在这里。

扩展新语言只需新增一个 LanguageConfig 实例，无需改动生成器代码。
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class LanguageConfig:
    """CodeQL 语言的差异性配置。"""

    # ---- 基础标识 ----
    language: str = ""
    """语言标识: "cpp" | "python" """

    # ---- 测试用例 ----
    source_extensions: List[str] = field(default_factory=list)
    """测试用例文件扩展名，如 [".cpp", ".c"] 或 [".py"] """

    # ---- CodeQL CLI ----
    codeql_language_flag: str = ""
    """codeql database create --language=... 的参数: "cpp" | "python" """

    database_build_command: str = ""
    """构建 database 的编译命令模板，{case_path} 会被替换。
    C++: "gcc -c {case_path}"，Python 等解释型语言不需要（为空则跳过 --command）"""

    # ---- qlpack ----
    qlpack_dependency: str = ""
    """qlpack.yml 中的依赖声明: 'codeql/cpp-all: "*"' | 'codeql/python-all: "*"' """

    # ---- 查询模板 ----
    ql_import_statement: str = ""
    """.ql 查询模板头的 import 语句: "import cpp" | "import python" """

    # ---- LLM 交互 ----
    code_block_marker: str = ""
    """LLM 回答中代码块的语言标记: "cpp" | "python" """

    # ---- 检索策略 ----
    retrieval_mode: str = "legacy"
    """"legacy" = 复用现有 C++ 三种检索（.pt + ChromaDB 混合），
       "chromadb" = 全部走 ChromaDB multi-collection"""


# ── C++ 配置 ──────────────────────────────────────────────

CPP_CONFIG = LanguageConfig(
    language="cpp",
    source_extensions=[".cpp", ".c"],
    codeql_language_flag="cpp",
    database_build_command="gcc -c {case_path}",
    qlpack_dependency='codeql/cpp-all: "*"',
    ql_import_statement="import cpp",
    code_block_marker="cpp",
    retrieval_mode="legacy",
)

# ── Python 配置 ───────────────────────────────────────────

PYTHON_CONFIG = LanguageConfig(
    language="python",
    source_extensions=[".py"],
    codeql_language_flag="python",
    database_build_command="",          # Python 无需编译，不传 --command
    qlpack_dependency='codeql/python-all: "*"',
    ql_import_statement="import python",
    code_block_marker="python",
    retrieval_mode="chromadb",
)


# ── 快捷查找 ──────────────────────────────────────────────

def get_language_config(language: str) -> LanguageConfig:
    """按名称获取语言配置。"""
    mapping = {
        "cpp": CPP_CONFIG,
        "python": PYTHON_CONFIG,
    }
    if language not in mapping:
        raise ValueError(f"Unsupported language: {language}. Supported: {list(mapping.keys())}")
    return mapping[language]
