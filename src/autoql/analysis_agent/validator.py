"""Deterministic validation and static evidence binding for Analysis V2."""
import json
import re
import subprocess

from pydantic import ValidationError

from .evidence_registry import location_key, raw_location
from .schemas import AnalysisBrief, VulnerabilitySpec
from autoql.timing import timed


class SpecValidationError(ValueError):
    def __init__(self, issues):
        self.issues = issues
        super().__init__('; '.join(f"{x['path']}: {x['message']}" for x in issues))


class AnalysisBriefRecoveryError(ValueError):
    """Raised when ordinary assistant text cannot be recovered unambiguously."""


def issue(path, code, message, expected=None, actual=None):
    value = {'path': path, 'code': code, 'message': message}
    if expected is not None:
        value['expected'] = expected
    if actual is not None:
        value['actual'] = actual
    return value


def parse_json(text):
    """Shared Query-Agent parser retained independently of the Analysis schema."""
    matches = re.findall(r'```json\s*([\s\S]*?)```', text)
    return json.loads(matches[-1] if matches else text.strip())


def _balanced_json_objects(text):
    """Yield top-level JSON-object substrings while respecting quoted braces."""
    start = None
    depth = 0
    quoted = False
    escaped = False
    for index, char in enumerate(text):
        if start is None:
            if char == '{':
                start = index
                depth = 1
                quoted = False
                escaped = False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                yield text[start:index + 1]
                start = None


def recover_analysis_brief_text(text):
    """Recover one AnalysisBrief candidate from a text-only model response.

    Explicit wrappers are considered first, followed by balanced JSON objects.
    Candidates are deduplicated after JSON decoding. If several candidates are
    present, exactly one must satisfy the AnalysisBrief schema; otherwise the
    response is ambiguous and is rejected.
    """
    if not isinstance(text, str) or not text.strip():
        raise AnalysisBriefRecoveryError('final assistant message has no text')

    candidates = [text.strip()]
    candidates.extend(re.findall(
        r'```(?:json)?\s*([\s\S]*?)```', text, flags=re.IGNORECASE))
    candidates.extend(re.findall(
        r'<AnalysisBrief\b[^>]*>\s*([\s\S]*?)\s*</AnalysisBrief>',
        text, flags=re.IGNORECASE))
    candidates.extend(_balanced_json_objects(text))

    decoded = []
    seen = set()
    for candidate in candidates:
        try:
            value = json.loads(candidate.strip())
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(value, dict):
            continue
        canonical = json.dumps(value, ensure_ascii=False, sort_keys=True,
                               separators=(',', ':'))
        if canonical not in seen:
            seen.add(canonical)
            decoded.append(value)

    if not decoded:
        raise AnalysisBriefRecoveryError(
            'no complete JSON object found in final assistant message')
    if len(decoded) == 1:
        # Return the raw object so the normal validate_brief path can report
        # schema and evidence-location issues through its existing repair loop.
        return decoded[0]

    valid = []
    for value in decoded:
        try:
            valid.append(AnalysisBrief.model_validate(value))
        except ValidationError:
            pass
    if len(valid) == 1:
        return valid[0]
    raise AnalysisBriefRecoveryError(
        'multiple distinct JSON objects found in final assistant message')


def _parse(value):
    try:
        return value if isinstance(value, AnalysisBrief) else AnalysisBrief.model_validate(value)
    except ValidationError as exc:
        raise SpecValidationError([
            issue('.'.join(str(part) for part in error['loc']) or '$', error['type'],
                  error['msg'], actual=error.get('input'))
            for error in exc.errors(include_url=False)
        ]) from exc


def _location_issues(brief):
    problems = []
    ids = [entry.id for entry in brief.evidence]
    if any(not value.strip() for value in ids):
        problems.append(issue('evidence', 'blank_id', 'Evidence IDs must not be blank'))
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        problems.append(issue('evidence', 'duplicate_id', 'Evidence IDs must be unique', actual=duplicates))
    keys = [location_key(entry) for entry in brief.evidence]
    if len(set(keys)) != len(keys):
        problems.append(issue('evidence', 'duplicate_location',
                              'Evidence locations must not be repeated'))
    if not any(entry.revision == 'buggy' for entry in brief.evidence):
        problems.append(issue('evidence', 'missing_buggy_evidence',
                              'At least one buggy evidence location is required'))
    return problems


def validate_brief(value, registry):
    """Validate explorer coordinates and materialize their immutable source text."""
    brief = _parse(value)
    problems = _location_issues(brief)
    if problems:
        raise SpecValidationError(problems)
    try:
        registry.materialize(brief.evidence)
    except (KeyError, TypeError, UnicodeDecodeError, ValueError,
            OSError, subprocess.CalledProcessError) as exc:
        raise SpecValidationError([
            issue('evidence', 'invalid_source_location', str(exc))
        ]) from exc
    return brief


def enriched_brief(brief, registry):
    return {
        'vulnerability_summary': brief.vulnerability_summary,
        'evidence': [registry.entries[entry.id] for entry in brief.evidence],
    }


@timed('analysis.spec_validation')
def finalize(value, original_brief, registry):
    """Accept only composer-selected original locations and reattach canonical code."""
    composed = _parse(value)
    problems = _location_issues(composed)
    allowed = {location_key(entry) for entry in original_brief.evidence}
    for index, entry in enumerate(composed.evidence):
        if location_key(entry) not in allowed:
            problems.append(issue(f'evidence[{index}]', 'altered_or_new_evidence',
                                  'Composer must use an unchanged AnalysisBrief evidence location'))
    if problems:
        raise SpecValidationError(problems)

    evidence = []
    for entry in composed.evidence:
        canonical = registry.entries.get(entry.id)
        if canonical is None or location_key(canonical) != location_key(entry):
            raise SpecValidationError([
                issue('evidence', 'missing_canonical_evidence',
                      'Composer evidence has no matching statically extracted source')
            ])
        evidence.append(canonical)
    return VulnerabilitySpec.model_validate({
        'vulnerability_summary': composed.vulnerability_summary,
        'evidence': evidence,
    }).model_dump()
