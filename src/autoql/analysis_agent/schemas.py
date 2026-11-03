"""Minimal typed contracts for Analysis V2."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class EvidenceLocation(StrictModel):
    """Model-selected source coordinates; source code is filled by the program."""

    id: str = Field(min_length=1)
    revision: Literal['buggy', 'fix']
    file: str = Field(min_length=1)
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    @model_validator(mode='after')
    def ordered_lines(self):
        if self.end_line < self.start_line:
            raise ValueError('end_line must be greater than or equal to start_line')
        return self


class Evidence(EvidenceLocation):
    """A location enriched with immutable source text from its Git revision."""

    code: str = Field(min_length=1)


class AnalysisBrief(StrictModel):
    """The only structured output accepted from explorer and composer models."""

    vulnerability_summary: str = Field(min_length=1)
    evidence: list[EvidenceLocation] = Field(min_length=1)


class VulnerabilitySpec(StrictModel):
    """Final persisted result after static evidence materialization."""

    vulnerability_summary: str = Field(min_length=1)
    evidence: list[Evidence] = Field(min_length=1)
