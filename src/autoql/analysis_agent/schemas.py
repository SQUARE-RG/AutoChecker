"""Typed contracts for the analysis hand-off and vulnerability specification."""
from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator


AnalysisKind: TypeAlias = Literal[
    'taint_tracking', 'local_data_flow', 'structural_pattern',
    'control_flow_guard', 'stateful_protocol', 'configuration', 'fallback',
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class AnalysisFact(StrictModel):
    description: str = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)
    expression: str | None = None
    pattern: str | None = None

    @model_validator(mode='after')
    def expression_or_pattern(self):
        if not (self.expression or self.pattern):
            raise ValueError('analysis fact needs expression or pattern')
        return self


class AnalysisBrief(StrictModel):
    """Small, structured boundary between repository exploration and spec composition."""

    status: Literal['finding', 'no_security_finding', 'needs_evidence', 'unsupported']
    reason: str | None = None
    vulnerability_name: str | None = None
    root_cause: str | None = None
    fix_summary: str | None = None
    analysis_kind: AnalysisKind | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    key_facts: list[AnalysisFact] = Field(default_factory=list)

    @model_validator(mode='after')
    def status_contract(self):
        if self.status == 'finding':
            required = (self.vulnerability_name, self.root_cause, self.fix_summary,
                        self.analysis_kind, self.evidence_ids, self.key_facts)
            if not all(required):
                raise ValueError('finding brief needs name, root cause, fix, kind, evidence and facts')
        elif not self.reason:
            raise ValueError('terminal analysis brief needs a reason')
        return self


class SemanticEntry(StrictModel):
    description: str = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)
    expression: str | None = None
    pattern: str | None = None
    api: str | None = None
    node_role: str | None = None
    argument_index: int | None = Field(default=None, ge=0)

    @model_validator(mode='after')
    def expression_or_pattern(self):
        if not (self.expression or self.pattern):
            raise ValueError('semantic entry needs expression or pattern')
        return self


class TaintTrackingModel(StrictModel):
    sources: list[SemanticEntry]
    sinks: list[SemanticEntry]
    barriers: list[SemanticEntry]
    additional_steps: list[SemanticEntry]


class LocalDataFlowModel(StrictModel):
    scope: SemanticEntry
    flow_semantics: Literal['taint', 'value_preserving']
    origins: list[SemanticEntry]
    targets: list[SemanticEntry]
    local_steps: list[SemanticEntry]
    excluded_patterns: list[SemanticEntry]


class StructuralPatternModel(StrictModel):
    required_patterns: list[SemanticEntry]
    context_constraints: list[SemanticEntry]
    excluded_patterns: list[SemanticEntry]
    report_location: str = Field(min_length=1)


class ControlFlowGuardModel(StrictModel):
    sensitive_operations: list[SemanticEntry]
    required_guards: list[SemanticEntry]
    subject_relation: SemanticEntry
    guard_relation: SemanticEntry
    invalidation_conditions: list[SemanticEntry]
    report_location: str = Field(min_length=1)


class StatefulProtocolModel(StrictModel):
    subject: SemanticEntry
    initial_states: list[SemanticEntry]
    transitions: list[SemanticEntry]
    event_order: SemanticEntry
    invalid_sequences: list[SemanticEntry]
    terminal_effects: list[SemanticEntry]
    report_location: str = Field(min_length=1)


class ConfigurationModel(StrictModel):
    declarations: list[SemanticEntry]
    readers: list[SemanticEntry]
    unsafe_values: list[SemanticEntry]
    safe_values: list[SemanticEntry]
    precedence: list[SemanticEntry]
    effects: list[SemanticEntry]
    propagation: list[SemanticEntry]
    report_location: str = Field(min_length=1)


class SpecBase(StrictModel):
    schema_version: Literal['1.0']
    language: Literal['java']
    vulnerability_name: str = Field(min_length=1)
    vulnerability_summary: str = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)


class TaintTrackingSpec(SpecBase):
    analysis_kind: Literal['taint_tracking']
    model: TaintTrackingModel


class FallbackSpec(SpecBase):
    analysis_kind: Literal['fallback']
    model: TaintTrackingModel


class LocalDataFlowSpec(SpecBase):
    analysis_kind: Literal['local_data_flow']
    model: LocalDataFlowModel


class StructuralPatternSpec(SpecBase):
    analysis_kind: Literal['structural_pattern']
    model: StructuralPatternModel


class ControlFlowGuardSpec(SpecBase):
    analysis_kind: Literal['control_flow_guard']
    model: ControlFlowGuardModel


class StatefulProtocolSpec(SpecBase):
    analysis_kind: Literal['stateful_protocol']
    model: StatefulProtocolModel


class ConfigurationSpec(SpecBase):
    analysis_kind: Literal['configuration']
    model: ConfigurationModel


VulnerabilitySpec = Annotated[
    TaintTrackingSpec | FallbackSpec | LocalDataFlowSpec | StructuralPatternSpec |
    ControlFlowGuardSpec | StatefulProtocolSpec | ConfigurationSpec,
    Field(discriminator='analysis_kind'),
]

SPEC_SCHEMAS = {
    'taint_tracking': TaintTrackingSpec,
    'fallback': FallbackSpec,
    'local_data_flow': LocalDataFlowSpec,
    'structural_pattern': StructuralPatternSpec,
    'control_flow_guard': ControlFlowGuardSpec,
    'stateful_protocol': StatefulProtocolSpec,
    'configuration': ConfigurationSpec,
}

MODEL_FIELDS = {
    kind: list(schema.model_fields['model'].annotation.model_fields)
    for kind, schema in SPEC_SCHEMAS.items()
}

REQUIRED_NONEMPTY = {
    'taint_tracking': ['sources', 'sinks'], 'fallback': ['sources', 'sinks'],
    'local_data_flow': ['scope', 'origins', 'targets'],
    'structural_pattern': ['required_patterns'],
    'control_flow_guard': ['sensitive_operations', 'required_guards', 'subject_relation', 'guard_relation'],
    'stateful_protocol': ['subject', 'initial_states', 'transitions', 'event_order'],
    'configuration': ['readers', 'unsafe_values', 'effects'],
}
