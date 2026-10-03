"""Query Server 2 protocol as used by vscode-codeql v1.17.8."""
STATUS = {0: 'ok', 1: 'evaluation_error', 2: 'compile_error', 3: 'resource_exhausted',
          4: 'cancelled', 5: 'evaluation_error', 6: 'evaluation_error'}


def compilation_target(position, count_only=False):
    return {'quickEval': {'quickEvalPos': position, 'countOnly': count_only}}


def position_encoding(cli_version, configured='auto'):
    """2.23.3 compiler selection uses code points despite the TS UTF-16 contract.

    Verified using non-BMP text before a formula in a CRLF QL document. Do not
    retry alternative ranges: use an explicit version capability, recorded per probe.
    """
    if configured != 'auto': return configured
    return 'codepoint' if cli_version == '2.23.3' else 'utf16'
