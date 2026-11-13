"""Pure node operations used by the query orchestration graph."""
import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NeedsEvidenceRequest(BaseModel):
    """The only non-query response accepted during initial generation."""

    model_config = ConfigDict(extra='forbid')
    status: Literal['needs_evidence']
    reason: str = Field(min_length=1, max_length=4000)

    @field_validator('reason')
    @classmethod
    def nonblank_reason(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('reason must not be blank')
        return value


def extract_needs_evidence(text):
    """Parse an exclusive raw or JSON-fenced needs-evidence response."""
    stripped = text.strip()
    fenced = re.fullmatch(r'```json\s*([\s\S]*?)```', stripped)
    payload = fenced.group(1).strip() if fenced else stripped
    try:
        value = json.loads(payload)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError('Not a needs_evidence JSON response') from exc
    try:
        return NeedsEvidenceRequest.model_validate(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid needs_evidence response: ' + str(exc)) from exc


def extract_query(text):
    # The label is preferred, but a single typed fenced block is equally
    # unambiguous. Normalize only the envelope; never repair generated QL here.
    matches = re.findall(r'```(?:query|ql|codeql)\s*([\s\S]*?)```', text)
    all_blocks = re.findall(r'```[^\n]*\n[\s\S]*?```', text)
    placeholders = (
        '{{', '[Vulnerability ', '[Description ', '[Numeric ',
        '[stable-query-id]', '[AST node ', '[Semantic ', '[Source ',
        '[Sensitive ', '[Sanitized ', '[Evidenced ', '[Alert ', '[doc ',
        '### Search:', 'Code Example', '**Type**', '**Path**',
    )
    if (len(matches) != 1 or len(all_blocks) != 1 or
            any(marker in matches[0] for marker in placeholders) or
            len(matches[0].strip()) < 50):
        raise ValueError(
            'Return exactly one complete ```query fenced block without '
            'placeholders or additional text.')
    query = matches[0].strip() + '\n'
    if not re.search(r'@kind\s+(?:path-problem|problem)\b', query) or 'select' not in query:
        raise ValueError('Missing query metadata or select')
    return query
