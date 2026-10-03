"""Framework-independent public contracts. Coordinates are 1-based code points."""
from dataclasses import dataclass, field
import math
from typing import Literal


class QuickEvalError(Exception):
    def __init__(self, status, message, **details):
        super().__init__(message)
        self.status, self.details = status, details


@dataclass(frozen=True)
class SourceRange:
    start_line: int
    start_column: int
    end_line: int
    end_column: int


@dataclass(frozen=True)
class RangeTarget:
    range: SourceRange
    file_id: str | None = None
    expected_revision: str | None = None


@dataclass(frozen=True)
class SnippetTarget:
    text: str
    file_id: str | None = None
    expected_revision: str | None = None


@dataclass(frozen=True)
class SymbolTarget:
    qualified_name: str
    arity: int | None = None
    symbol_kind: str | None = None
    file_id: str | None = None
    expected_revision: str | None = None


@dataclass(frozen=True)
class EvaluationRequest:
    query_id: str
    expected_revision: str
    database: str
    target: RangeTarget | SnippetTarget | SymbolTarget
    mode: Literal['sample', 'count'] = 'sample'
    sample_limit: int = 8
    timeout_seconds: float = 120


@dataclass(frozen=True)
class Document:
    query_id: str
    file_id: str
    path: str
    revision: str


@dataclass
class SessionConfig:
    codeql_binary: str
    artifact_dir: str
    allowed_roots: list[str]
    databases: dict[str, str]
    database_revisions: dict[str, str] = field(default_factory=dict)
    additional_packs: list[str] = field(default_factory=list)
    extension_packs: list[str] = field(default_factory=list)
    position_encoding: str = "auto"
    threads: int = 2
    ram_mb: int = 4096
    request_timeout_seconds: float = 120
    session_timeout_seconds: float = 600
    max_requests: int = 12
    cancel_grace_seconds: float = 3
    max_page_rows: int = 50
    max_tool_bytes: int = 16384

    def __post_init__(self):
        if self.position_encoding not in ('auto','utf16','codepoint'):
            raise ValueError('position_encoding must be auto, utf16 or codepoint')
        for name in ('threads', 'ram_mb', 'request_timeout_seconds', 'session_timeout_seconds',
                     'max_requests', 'cancel_grace_seconds', 'max_page_rows', 'max_tool_bytes'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be positive')
        for name in ('threads', 'ram_mb', 'max_requests', 'max_page_rows', 'max_tool_bytes'):
            if not isinstance(getattr(self, name), int):
                raise ValueError(f'{name} must be an integer')
        if self.max_tool_bytes < 1024:
            raise ValueError('max_tool_bytes must be at least 1024')
        if not self.allowed_roots or not self.databases:
            raise ValueError('allowed_roots and databases are required')


def target_from_dict(value):
    value = dict(value)
    kind = value.pop('kind')
    if kind == 'range':
        value['range'] = SourceRange(**value['range'])
        return RangeTarget(**value)
    if kind == 'snippet':
        return SnippetTarget(**value)
    if kind == 'symbol':
        return SymbolTarget(**value)
    raise ValueError('target kind must be range, snippet, or symbol')
