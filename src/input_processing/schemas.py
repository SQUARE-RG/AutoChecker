from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DocumentBlock:
    block_id: str
    page: int
    type: str
    text: str
    bbox: list[float] | None = None
    confidence: float | None = None
    order: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "DocumentBlock":
        return cls(**value)


@dataclass
class RuleExample:
    type: str
    code: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RuleExample":
        return cls(type=str(value["type"]), code=str(value["code"]))


@dataclass
class RuleCandidate:
    rule_id: str | None
    main_title: str
    description: str
    rule_type: str
    examples: list[RuleExample] = field(default_factory=list)
    source_chunks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RuleCandidate":
        known = {field_.name for field_ in cls.__dataclass_fields__.values()}
        normalized = {key: val for key, val in value.items() if key in known}
        normalized["examples"] = [
            RuleExample.from_dict(item) for item in value.get("examples", [])
        ]
        return cls(**normalized)


@dataclass
class ChunkExtractionResult:
    chunk_id: str
    rules: list[RuleCandidate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "rules": [rule.to_dict() for rule in self.rules],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ChunkExtractionResult":
        return cls(
            chunk_id=str(value["chunk_id"]),
            rules=[RuleCandidate.from_dict(item) for item in value.get("rules", [])],
        )
