"""Structural and evidence-backed semantic validation for analysis output."""
import json
import re

from pydantic import BaseModel, ValidationError

from .schemas import AnalysisBrief, REQUIRED_NONEMPTY, SPEC_SCHEMAS
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
    matches = re.findall(r'```json\s*([\s\S]*?)```', text)
    return json.loads(matches[-1] if matches else text.strip())


def _raw(value):
    return value.model_dump(exclude_none=True) if isinstance(value, BaseModel) else value


def validate_brief(value, registry):
    brief = value if isinstance(value, AnalysisBrief) else AnalysisBrief.model_validate(value)
    if brief.status != 'finding':
        return brief
    problems = []
    selected = set(brief.evidence_ids)
    unknown = sorted(selected - set(registry.entries))
    if unknown:
        problems.append(issue('evidence_ids', 'unknown_evidence',
            'Analysis brief references evidence that was not registered', actual=unknown))
    for index, fact in enumerate(brief.key_facts):
        missing = sorted(set(fact.evidence_ids) - selected)
        if missing:
            problems.append(issue(f'key_facts[{index}].evidence_ids', 'unselected_evidence',
                'Key fact must cite evidence selected by the brief', actual=missing))
    known = selected & set(registry.entries)
    if known and not any(registry.entries[key]['revision'] == 'buggy' for key in known):
        problems.append(issue('evidence_ids', 'missing_buggy_evidence',
            'A finding needs buggy evidence for detection'))
    if problems:
        raise SpecValidationError(problems)
    return brief


def validate_structure(value):
    raw = _raw(value)
    if not isinstance(raw, dict):
        raise SpecValidationError([issue('$', 'invalid_type', 'Spec must be an object')])
    kind = raw.get('analysis_kind')
    schema = SPEC_SCHEMAS.get(kind)
    if schema is None:
        raise SpecValidationError([issue('analysis_kind', 'invalid_enum',
            'Unknown analysis kind', expected=sorted(SPEC_SCHEMAS), actual=kind)])
    try:
        return schema.model_validate(raw)
    except ValidationError as exc:
        problems = []
        for error in exc.errors(include_url=False):
            path = '.'.join(str(part) for part in error['loc']) or '$'
            problems.append(issue(path, error['type'], error['msg'], actual=error.get('input')))
        raise SpecValidationError(problems) from exc


def _semantic_entries(value, path='$'):
    if isinstance(value, dict):
        if 'description' in value:
            yield path, value
        for key, child in value.items():
            if key not in ('api', 'evidence_ids'):
                yield from _semantic_entries(child, f'{path}.{key}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _semantic_entries(child, f'{path}[{index}]')


@timed('analysis.spec_validation')
def finalize(value, registry):
    raw = _raw(value)
    if isinstance(raw, dict) and raw.get('status') in (
        'no_security_finding', 'needs_evidence', 'unsupported'
    ):
        if not raw.get('reason'):
            raise SpecValidationError([issue('reason', 'missing', 'Terminal status needs a reason')])
        return raw

    parsed = validate_structure(raw)
    raw = parsed.model_dump(exclude_none=True)
    kind, model = raw['analysis_kind'], raw['model']
    selected = raw['evidence_ids']
    selected_set = set(selected)
    problems = []

    unknown = sorted(selected_set - set(registry.entries))
    if unknown:
        problems.append(issue('evidence_ids', 'unknown_evidence',
            'Use registered evidence IDs only', actual=unknown))

    for key in REQUIRED_NONEMPTY[kind]:
        if not model[key]:
            problems.append(issue(f'model.{key}', 'empty_required_field',
                'Required detection condition must not be empty'))

    if kind == 'stateful_protocol' and not (
        model['invalid_sequences'] or model['terminal_effects']
    ):
        problems.append(issue('model', 'missing_protocol_failure',
            'Stateful protocol needs invalid_sequences or terminal_effects'))

    for path, entry in _semantic_entries(model, 'model'):
        citations = set(entry['evidence_ids'])
        missing = sorted(citations - selected_set)
        if missing:
            problems.append(issue(path + '.evidence_ids', 'unselected_evidence',
                'Semantic entry must cite evidence selected by the spec', actual=missing))
        for field in ('expression', 'pattern'):
            if re.search(r'\bexists\s*\([^)]*\|', str(entry.get(field, ''))):
                problems.append(issue(path + '.' + field, 'generated_ql',
                    'Analysis model must not contain generated QL'))

    known = selected_set & set(registry.entries)
    if known and not any(registry.entries[key]['revision'] == 'buggy' for key in known):
        problems.append(issue('evidence_ids', 'missing_buggy_evidence',
            'Spec needs buggy evidence for detection'))

    if problems:
        raise SpecValidationError(problems)

    result = dict(raw)
    result.pop('evidence_ids')
    result['evidence'] = [registry.entries[key] for key in dict.fromkeys(selected)]
    return result
