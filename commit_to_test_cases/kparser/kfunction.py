from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from multiprocessing import Pool
from pathlib import Path

from tree_sitter import Node
from kparser.kparser import KParser
# from .kparser import KParser

CURR = Path(__file__).parent


@dataclass
class KernelFunction:
    file_path: Path
    # 这里的Node是tree-sitter的Node类型，kaprser.py中实现了将文件和代码转换成Node的功能
    node: Node
    code: str
    name: str

    def __init__(
        self,
        file_path: Path,
        node: Node,
    ):
        self.file_path = file_path
        self.node = node

        if node.type != "function_definition":
            raise ValueError("Node is not a function definition")
        self.code = node.text.decode("utf-8")
        self.name = self.__find_name(node)
        self.start_line = node.start_point[0]
        self.end_line = node.end_point[0]
    # 在 function_definition 节点内部找到函数标识符并返回其文本。
    def __find_name(self, node: Node) -> str:
        children = [c for c in node.children]
        types = [c.type for c in children]
        if "function_declarator" in types:
            decl = children[types.index("function_declarator")]
            for c in decl.children:
                if c.type == "identifier":
                    return c.text.decode("utf-8")
            # If no identifier found, return empty string
            return ""
        elif "pointer_declarator" in types:
            return self.__find_name(children[types.index("pointer_declarator")])
        else:
            return ""
    # 判断给定节点是否代表一个函数定义（用于递归遍历时辨认叶子函数节点）。
    def __is_function(node: Node) -> bool:
        if node.type != "function_definition":
            return False
        types = [c.type for c in node.children]
        return "function_declarator" in types or "pointer_declarator" in types
    # 返回函数的起始/结束行号。
    def get_line_numbers(self) -> int:
        return self.start_line, self.end_line
    # 从给定文件（或给定节点）递归提取所有函数定义，返回 KernelFunction 列表。
    def from_file(
        fpath: Path,
        node: Node = None,
        rec_depth: int = 30,
        parser: KParser = None,
    ) -> list[KernelFunction]:
        if rec_depth <= 0:
            return []

        if parser is None:
            parser = KParser()
        if node is None:
            node = parser.parse_file(fpath)

        if KernelFunction.__is_function(node):
            return [KernelFunction(fpath, node)]
        elif node.children is not None:
            return list(
                chain.from_iterable(
                    [
                        KernelFunction.from_file(fpath, c, rec_depth - 1, parser)
                        for c in node.children
                    ]
                )
            )
        else:
            return []
    # 并行地对多个文件调用 from_file，汇总所有提取到的 KernelFunction 列表。
    def from_files(files: list[Path], num_procs: int = 20) -> list[KernelFunction]:
        with Pool(num_procs) as p:
            results = p.map(KernelFunction.from_file, files)
            return list(chain.from_iterable(results))
