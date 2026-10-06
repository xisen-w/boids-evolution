"""Strict engineering stop rules; never alter confirmatory scoring rules."""
import random
import re


_MISSING_KEY = re.compile(r"KeyError: ['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]\Z")
_MISSING_ARGS = re.compile(r"TypeError: execute\(\) missing ([1-9][0-9]*) required "
                           r"(?:positional|keyword-only) arguments?: (.+)\Z")


def missing_parameter(error, names):
    """Recognize missing public kwargs, not arbitrary execution failures.

    This is only an error-shape check. The caller must independently verify
    the supplied-parameter path and inspect every signal error as well.
    """
    if not isinstance(error, str):
        return False
    match = _MISSING_KEY.fullmatch(error)
    if match:
        return match.group(1) in names
    match = _MISSING_ARGS.fullmatch(error)
    if match:
        args = re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'", match.group(2))
        return len(args) == int(match.group(1)) and set(args) <= set(names)
    if error.startswith('ValueError: '):
        body = error[len('ValueError: '):]
        missing = re.search(r'\b(?:missing|required)\b|\bmust be (?:provided|supplied)\b', body, re.I)
        words = set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', body))
        return bool(missing and words.intersection(names))
    return False


def verified_parametric_component(env, tool, entry, feedback, diagnostic=None):
    """Classify expected no-kwargs calls, never turn a failed task into a pass.

    Independently evaluate the supplied-parameter path. Ordinary generated-code
    errors stay failed outcomes; unknown/resource/security failures still stop.
    Freeze still requires correctness and excludes
    an incorrect parametric tool. Only TARGET NONE and recognized missing public
    parameters qualify, regardless of Python's exception spelling.
    """
    audit = diagnostic if diagnostic is not None else {}
    audit.update(status='not_classified', primitive_verdicts={})
    error = feedback.removeprefix('raised ') if feedback.startswith('raised ') else ''
    if entry.get('target') is not None:
        return None
    declarations = entry.get('implements') or []
    if not declarations or any(p not in env.m.PRIMITIVES for p in declarations):
        return None
    parameters = set()
    for primitive in sorted(set(declarations)):
        parameters.update(env.m.PRIMITIVES[primitive][1](random.Random(0)))
    if not missing_parameter(error, parameters):
        audit['status'] = 'unexpected_missing_key'
        return None
    verified = {}
    for primitive in sorted(set(declarations)):
        # Use the same independent primitive oracle as the frozen-library path.
        verdict = env.verify_primitive(tool, primitive)
        # Keep failures too: otherwise a semantic mismatch is hidden behind the
        # earlier public no-kwargs KeyError. This audit is never shown to agents.
        audit['primitive_verdicts'][primitive] = verdict
        if verdict.get('crashed', 0) and (verdict.get('passed') or not ordinary_solver_code_error(verdict)):
            audit['status'] = 'primitive_verification_failed'
            return None
        if verdict.get('passed'):
            verified[primitive] = verdict
    correct = len(verified) == len(set(declarations))
    audit['status'] = ('verified_parametric_component' if correct
                       else 'parametric_implementation_failure')
    return {'status': audit['status'], 'semantic_passed': correct,
            'verified_primitives': verified,
            'parameter_names': sorted(parameters), 'public_error_classified': True,
            'signal_errors_classified': 0}


class SmokeStop(RuntimeError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def verdict_has_execution_error(verdict):
    # A wrong answer is a normal task outcome, not an engineering failure.
    return bool(verdict and verdict.get('crashed', 0))


def ordinary_model_code_error(error):
    """Generated Python errors only; not transport, permission, or resource failures."""
    kinds = ('KeyError|TypeError|ValueError|IndexError|NameError|AttributeError|'
             'ZeroDivisionError|SyntaxError|IndentationError|ImportError|'
             'ModuleNotFoundError|UnboundLocalError')
    return isinstance(error, str) and bool(re.match(r'^(?:' + kinds + r'):', error))


def ordinary_solver_code_error(verdict):
    """Known Python mistakes are failed answers, not broken infrastructure.

    Do not classify timeout/resource failures, sandbox permission failures,
    missing diagnostics, or unknown runtime errors this way. Infrastructure
    exceptions propagate before a verdict is returned by the harness.
    """
    if not verdict_has_execution_error(verdict):
        return False
    details = verdict.get('details') or []
    crashes = [s for s in details if ': crash ' in s]
    pattern = re.compile(r'^seed [0-9]+: crash RuntimeError: (.*)')
    return (len(crashes) == verdict['crashed']
            and all(pattern.match(s) and ordinary_model_code_error(pattern.match(s).group(1))
                    for s in crashes))
