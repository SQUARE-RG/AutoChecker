"""Complete, schema-valid examples selected one-at-a-time for spec composition."""


def entry(description, expression=None, pattern=None, role=None, argument_index=None):
    value = {'description': description, 'evidence_ids': ['E1']}
    if expression:
        value['expression'] = expression
    if pattern:
        value['pattern'] = pattern
    if role:
        value['node_role'] = role
    if argument_index is not None:
        value['argument_index'] = argument_index
    return value


BASE = {
    'schema_version': '1.0', 'language': 'java',
    'vulnerability_name': 'Illustrative vulnerability',
    'vulnerability_summary': 'A concise evidence-backed mechanism used only as a formatting example.',
    'evidence_ids': ['E1'],
}

SPEC_EXAMPLES = {
    'taint_tracking': {**BASE, 'analysis_kind': 'taint_tracking', 'model': {
        'sources': [entry('Untrusted request value', 'request.getParameter("path")', role='source')],
        'sinks': [entry('Filesystem write path argument', 'new FileOutputStream(path)', role='sink', argument_index=0)],
        'barriers': [],
        'additional_steps': [entry('Helper returns the path value', 'normalizeUserPath(path)')],
    }},
    'fallback': {**BASE, 'analysis_kind': 'fallback', 'model': {
        'sources': [entry('Untrusted input value', 'request.getParameter("value")', role='source')],
        'sinks': [entry('Dangerous operation argument', 'execute(value)', role='sink', argument_index=0)],
        'barriers': [], 'additional_steps': [],
    }},
    'local_data_flow': {**BASE, 'analysis_kind': 'local_data_flow', 'model': {
        'scope': entry('Callable containing input and execution', 'void run(HttpServletRequest request)', role='callable'),
        'flow_semantics': 'value_preserving',
        'origins': [entry('Request parameter return value', 'request.getParameter("cmd")', role='source')],
        'targets': [entry('Command execution argument', 'runtime.exec(cmd)', role='sink', argument_index=0)],
        'local_steps': [], 'excluded_patterns': [],
    }},
    'structural_pattern': {**BASE, 'analysis_kind': 'structural_pattern', 'model': {
        'required_patterns': [entry('DTD support is enabled', 'factory.setProperty(SUPPORT_DTD, true)')],
        'context_constraints': [entry('The same factory parses XML', 'factory.createXMLStreamReader(input)')],
        'excluded_patterns': [], 'report_location': 'dangerous configuration call',
    }},
    'control_flow_guard': {**BASE, 'analysis_kind': 'control_flow_guard', 'model': {
        'sensitive_operations': [entry('Account deletion', 'deleteAccount(user)', role='dangerous operation')],
        'required_guards': [entry('Authorization decision', 'isAdmin(user)', role='guard')],
        'subject_relation': entry('Guard and operation concern the same user', pattern='the checked user is the deleted user'),
        'guard_relation': entry('Operation must be controlled by the successful guard branch', pattern='the true guard branch controls the operation'),
        'invalidation_conditions': [], 'report_location': 'sensitive operation',
    }},
    'stateful_protocol': {**BASE, 'analysis_kind': 'stateful_protocol', 'model': {
        'subject': entry('Tracked resource instance', 'resource'),
        'initial_states': [entry('Opening creates the live state', 'Resource resource = open()')],
        'transitions': [entry('Close changes live to closed', 'resource.close()')],
        'event_order': entry('Events follow control flow for the same resource', pattern='same-resource events in control-flow order'),
        'invalid_sequences': [],
        'terminal_effects': [entry('A method exit is reached while still live', pattern='method exits with resource in live state')],
        'report_location': 'resource acquisition',
    }},
    'configuration': {**BASE, 'analysis_kind': 'configuration', 'model': {
        'declarations': [entry('TLS verification key', 'tls.verify')],
        'readers': [entry('Boolean setting with a default', 'config.getBoolean("tls.verify", false)')],
        'unsafe_values': [entry('Verification disabled', 'false')],
        'safe_values': [entry('Verification enabled', 'true')],
        'precedence': [entry('Explicit setting overrides the default', pattern='explicit configuration value precedes the default')],
        'effects': [entry('TLS client consumes the verification setting', 'client.setVerifyPeer(verifyPeer)')],
        'propagation': [entry('Read value reaches the client setter', 'verifyPeer')],
        'report_location': 'unsafe TLS client configuration',
    }},
}
