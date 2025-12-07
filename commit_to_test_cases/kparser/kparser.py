import ctypes
from pathlib import Path

from tree_sitter import Language, Node, Parser

CURR = Path(__file__).parent
# 把指定 grammar（tree-sitter-cpp 目录）编译成共享库 build/my-languages.so。
Language.build_library(
    str(CURR / "build/my-languages.so"),
    [str(CURR / "tree-sitter-cpp")],
)


class KParser:
    def __init__(self):
        # Load the shared library
        #用 ctypes 动态加载刚生成的共享库（.so），返回底层 C 库句柄。
        lib = ctypes.CDLL(str(CURR / "build/my-languages.so"))

        # Get the language function pointer
        get_language = lib.tree_sitter_cpp
        get_language.restype = ctypes.c_void_p

        # Create language with pointer instead of path
        cpp_language = Language(get_language(), "cpp")
        parser = Parser()
        parser.set_language(cpp_language)
        self.parser = parser

    # 把文件内容编码为 UTF-8 bytes
    def parse_file(self, fpath: Path) -> Node:
        source_code = open(fpath, "r").read()
        tree = self.parser.parse(bytes(source_code, "utf8"))
        return tree.root_node

    # 把代码字符串编码为 UTF-8 bytes
    def parse_code(self, code: str) -> Node:
        tree = self.parser.parse(bytes(code, "utf8"))
        return tree.root_node
