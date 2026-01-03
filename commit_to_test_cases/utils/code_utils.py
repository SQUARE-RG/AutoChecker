import re
from typing import List, Sequence, Set

_C_KEYWORDS: Set[str] = {
    "if",
    "for",
    "while",
    "switch",
    "return",
    "sizeof",
    "else",
    "do",
    "case",
    "goto",
    "break",
    "continue",
    "struct",
    "enum",
    "union",
    "typedef",
    "static",
    "const",
    "volatile",
    "unsigned",
    "signed",
    "long",
    "short",
    "int",
    "float",
    "double",
    "char",
    "bool",
    "_Bool",
    "register",
    "inline",
    "restrict",
    "extern",
    "default",
}

_STANDARD_CALLS: Set[str] = {
    "malloc",
    "calloc",
    "free",
    "realloc",
    "memset",
    "memcpy",
    "printf",
    "fprintf",
    "puts",
    "scanf",
    "strcpy",
    "strlen",
    "strcmp",
    "exit",
    "abort",
}

_DEF_PATTERN = re.compile(
    r"^[\t ]*(?:[A-Za-z_]\w*(?:[\s\*]+))+?(?P<name>[A-Za-z_]\w*)\s*\([^;{]*\)\s*\{",
    re.MULTILINE,
)
_CALL_PATTERN = re.compile(r"([A-Za-z_]\w*)\s*\(", re.MULTILINE)
_UNDEF_REF_PATTERN = re.compile(r"undefined reference to '([^']+)'")
_IMPLICIT_DECL_PATTERN = re.compile(r"implicit declaration of function '([^']+)'")


def extract_function_definitions(code: str) -> Set[str]:
    return {match.group("name") for match in _DEF_PATTERN.finditer(code)}


def extract_function_calls(code: str) -> List[str]:
    calls: List[str] = []
    for match in _CALL_PATTERN.finditer(code):
        name = match.group(1)
        if not name or name[0].isdigit():
            continue
        calls.append(name)
    return calls


def collect_missing_symbols(code: str, allowed: Sequence[str] | None = None) -> Set[str]:
    allowed_set: Set[str] = set(allowed or [])
    defined = extract_function_definitions(code)
    allowed_set.update(defined)
    allowed_set.update(_STANDARD_CALLS)
    missing: Set[str] = set()
    for call in extract_function_calls(code):
        if call in allowed_set or call in _C_KEYWORDS:
            continue
        missing.add(call)
    return missing


def parse_compile_errors(log: str) -> Set[str]:
    missing: Set[str] = set()
    if not log:
        return missing
    missing.update(_UNDEF_REF_PATTERN.findall(log))
    missing.update(_IMPLICIT_DECL_PATTERN.findall(log))
    return missing


def slice_source_window(source: str, symbol: str, window: int = 20) -> str:
    lines = source.splitlines()
    for idx, line in enumerate(lines):
        if symbol in line:
            start = max(0, idx - window // 2)
            end = min(len(lines), idx + window // 2 + 1)
            return "\n".join(lines[start:end])
    return ""
