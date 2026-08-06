"""Collect class and predicate metadata from CodeQL C/C++ libraries."""

from __future__ import annotations

import argparse
import ctypes
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from tree_sitter import Language, Node, Parser

import tree_sitter_ql


def load_ql_language() -> Language:
	"""Instantiate the tree-sitter QL language from the packaged capsule."""
	get_pointer = ctypes.pythonapi.PyCapsule_GetPointer
	get_pointer.restype = ctypes.c_void_p
	get_pointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
	ptr = get_pointer(tree_sitter_ql.language(), b"tree_sitter.Language")
	return Language(ptr, "ql")


def normalize_ws(text: str) -> str:
	return " ".join(text.strip().split())


def clean_doc_comment(raw: str | None) -> str:
	if not raw:
		return ""
	text = raw.strip()
	if text.startswith("//"):
		lines = [line.lstrip("/ ") for line in text.splitlines()]
		return "\n".join(line.rstrip() for line in lines).strip()
	if text.startswith("/*"):
		text = text[2:-2]
	lines = []
	for line in text.splitlines():
		line = line.strip()
		if line.startswith("*"):
			line = line.lstrip("* ")
		lines.append(line.rstrip())
	return "\n".join(lines).strip()


def build_doc_text(nodes: Sequence[Node], source: str) -> Optional[str]:
	if not nodes:
		return None
	raw = "\n".join(node_text(n, source) for n in nodes)
	cleaned = clean_doc_comment(raw)
	return cleaned or None


def body_text(node: Optional[Node], source: str) -> str:
	if node is None:
		return ""
	text = source[node.start_byte : node.end_byte].strip()
	if text.startswith("{") and text.endswith("}"):
		text = text[1:-1].strip()
	return text


def node_text(node: Optional[Node], source: str) -> str:
	if node is None:
		return ""
	return source[node.start_byte : node.end_byte]


def find_child(node: Node, type_name: str) -> Optional[Node]:
	for child in node.children:
		if child.type == type_name:
			return child
	return None


def is_private(annotation_texts: Sequence[str]) -> bool:
	return any(re.search(r"\bprivate\b", ann) for ann in annotation_texts)


def collect_params(container: Node, source: str) -> List[Dict[str, str]]:
	params: List[Dict[str, str]] = []
	for child in container.children:
		if child.type != "varDecl":
			continue
		type_node = next((c for c in child.children if c.type == "typeExpr"), None)
		if type_node is None:
			type_node = child.child_by_field_name("typeExpr")
		name_node = next((c for c in child.children if c.type == "varName"), None)
		if name_node is None:
			name_node = child.child_by_field_name("varName")
		type_text = normalize_ws(node_text(type_node, source)) if type_node else ""
		name_text = normalize_ws(node_text(name_node, source)) if name_node else ""
		params.append({"type": type_text, "name": name_text})
	return params


def merge_docs(current: Optional[str], new: Optional[str]) -> Optional[str]:
	if not new:
		return current
	if not current:
		return new
	return f"{current}\n{new}"


@dataclass
class ModuleExtraction:
	predicates: List[Dict[str, Any]]
	classes: List[Dict[str, Any]]


class QLApiCollector:
	def __init__(self) -> None:
		self.parser = Parser()
		self.parser.set_language(load_ql_language())

	def collect(self, lib_root: Path) -> Dict[str, Any]:
		predicates: List[Dict[str, Any]] = []
		classes: List[Dict[str, Any]] = []
		for qll_path in sorted(lib_root.rglob("*.qll")):
			module = self._extract_module(qll_path)
			predicates.extend(module.predicates)
			classes.extend(module.classes)
		return {"predicate": predicates, "class": classes}

	def _build_signature(
		self,
		name: str,
		args: List[Dict[str, str]],
		return_type: Optional[str] = None,
		class_name: Optional[str] = None,
	) -> str:
		"""Construct a human-readable signature for predicates and methods.

		Examples:
		- predicate topLevel(int x, string y)
		- predicate MyClass::holds(int x)
		- ResultType MyClass::getResult(int x)
		"""
		params: List[str] = []
		for p in args:
			t = p.get("type", "").strip()
			n = p.get("name", "").strip()
			if t and n:
				params.append(f"{t} {n}")
			elif t:
				params.append(t)
			elif n:
				params.append(n)
		params_text = ", ".join(params)
		base = f"{name}({params_text})"
		if class_name:
			base = f"{class_name}::{base}"
		if return_type:
			return f"{return_type} {base}"
		return base

	def _extract_module(self, qll_path: Path) -> ModuleExtraction:
		source = qll_path.read_text(encoding="utf-8")
		tree = self.parser.parse(source.encode("utf-8"))
		predicates: List[Dict[str, Any]] = []
		classes: List[Dict[str, Any]] = []
		pending_doc: Optional[str] = None
		for member in tree.root_node.children:
			if member.type != "moduleMember":
				continue
			doc_nodes = [c for c in member.children if c.type == "qldoc"]
			ann_nodes = [c for c in member.children if c.type == "annotation"]
			content = [c for c in member.children if c.type not in {"qldoc", "annotation", "line_comment"}]
			doc_text = build_doc_text(doc_nodes, source)
			if not content:
				pending_doc = merge_docs(pending_doc, doc_text)
				continue
			node = content[0]
			annotations = [node_text(a, source).strip() for a in ann_nodes]
			doc = doc_text or pending_doc
			pending_doc = None
			if node.type == "classlessPredicate":
				if is_private(annotations):
					continue
				predicates.append(self._build_predicate(node, source, doc))
			elif node.type == "dataclass":
				classes.append(self._build_class(node, source, doc))
		return ModuleExtraction(predicates, classes)

	def _build_predicate(self, node: Node, source: str, doc: Optional[str]) -> Dict[str, Any]:
		name = normalize_ws(node_text(node.child_by_field_name("name"), source))
		params = collect_params(node, source)
		body_node = find_child(node, "body")
		return {
			"name": name,
			"args": params,
			"body": body_text(body_node, source),
			"comments": doc or "",
			"signature": self._build_signature(name, params, return_type="predicate"),
		}

	def _build_class(self, node: Node, source: str, doc: Optional[str]) -> Dict[str, Any]:
		class_name = normalize_ws(node_text(node.child_by_field_name("name"), source))
		extends = self._collect_extends(node, source)
		methods: List[Dict[str, Any]] = []
		predicates: List[Dict[str, Any]] = []
		pending_doc: Optional[str] = None
		for member in node.children:
			if member.type != "classMember":
				continue
			doc_nodes = [c for c in member.children if c.type == "qldoc"]
			ann_nodes = [c for c in member.children if c.type == "annotation"]
			definition = next((c for c in member.children if c.type not in {"qldoc", "annotation", "line_comment"}), None)
			doc_text = build_doc_text(doc_nodes, source)
			if definition is None:
				pending_doc = merge_docs(pending_doc, doc_text)
				continue
			annotations = [node_text(a, source).strip() for a in ann_nodes]
			member_doc = doc_text or pending_doc
			pending_doc = None
			if definition.type == "memberPredicate":
				entry, is_pred = self._build_member_predicate(definition, source, member_doc, class_name)
				if is_private(annotations):
					continue
				if is_pred:
					predicates.append(entry)
				else:
					methods.append(entry)
			elif definition.type == "charpred":
				if is_private(annotations):
					continue
				predicates.append(self._build_charpred(definition, source, member_doc, class_name))
		return {
			"className": class_name,
			"extends": extends,
			"comments": doc or "",
			"method": methods,
			"predicate": predicates,
		}

	def _collect_extends(self, node: Node, source: str) -> List[str]:
		results: List[str] = []
		capture = False
		for child in node.children:
			if child.type == "extends":
				capture = True
				continue
			if capture:
				if child.type == "typeExpr":
					results.append(normalize_ws(node_text(child, source)))
				elif child.type == "{":
					break
		return results

	def _build_member_predicate(
		self,
		node: Node,
		source: str,
		doc: Optional[str],
		class_name: Optional[str] = None,
	) -> tuple[Dict[str, Any], bool]:
		name = normalize_ws(node_text(node.child_by_field_name("name"), source))
		return_type = normalize_ws(node_text(node.child_by_field_name("returnType"), source))
		params = collect_params(node, source)
		body_node = find_child(node, "body")
		entry: Dict[str, Any] = {
			"name": name,
			"args": params,
			"body": body_text(body_node, source),
			"comments": doc or "",
			"signature": self._build_signature(name, params, return_type=return_type, class_name=class_name),
		}
		if return_type == "predicate":
			return entry, True
		entry["type"] = return_type
		return entry, False

	def _build_charpred(
		self,
		node: Node,
		source: str,
		doc: Optional[str],
		class_name: Optional[str] = None,
	) -> Dict[str, Any]:
		name_node = next((c for c in node.children if c.type == "className"), None)
		params = collect_params(node, source)
		body_node = node.child_by_field_name("body") or find_child(node, "body")
		pred_name = normalize_ws(node_text(name_node, source)) if name_node is not None else ""
		return {
			"name": pred_name,
			"args": params,
			"body": body_text(body_node, source),
			"comments": doc or "",
			"signature": self._build_signature(pred_name, params, class_name=class_name),
		}


def main() -> None:
	parser = argparse.ArgumentParser(description="Collect CodeQL API metadata")
	parser.add_argument(
		"--lib-root",
		type=Path,
		default=Path("codeql/cpp/ql/lib/semmle/code/cpp"),
		help="Path to the CodeQL C/C++ library root",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=Path("codeql_collect/codeql_api_collect/cpp_api.json"),
		help="Output JSON path",
	)
	args = parser.parse_args()

	collector = QLApiCollector()
	result = collector.collect(args.lib_root)
	args.output.parent.mkdir(parents=True, exist_ok=True)
	args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
	print(f"Extracted {len(result['predicate'])} predicates and {len(result['class'])} classes to {args.output}")


if __name__ == "__main__":
	main()
