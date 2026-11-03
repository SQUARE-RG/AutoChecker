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
