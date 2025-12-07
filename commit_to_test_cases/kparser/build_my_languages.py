from pathlib import Path
from tree_sitter import Language
#usage 在kparser目录下运行 python build_my_languages.py
# 这个脚本的目的是生成my_language.so文件，用于tree-sitter解析C++代码
# 调整下面的 grammar 路径为你的实际位置
repo_root = Path(__file__).resolve().parents[2]
grammar_dir = repo_root / "commit_to_test_cases" / "kparser" / "tree-sitter-cpp"

out_dir = Path(__file__).resolve().parent
out_dir.mkdir(parents=True, exist_ok=True)
lib_path = out_dir / "my-languages.so"

if not grammar_dir.exists():
    raise SystemExit(f"Grammar dir not found: {grammar_dir}")

# build
Language.build_library(
    str(lib_path),
    [str(grammar_dir)]
)

print("Built:", lib_path)