"""Trusted offline instrumentation, never a builder/solver prompt or tool edit.

Imports are wrapped after loading so aliases, relative imports and importlib
see the same execute wrapper. Identity replacement is conditional on BOTH
the caller's source identity and callee ID; other importers are unaffected.
The ordinary sandbox ACL/profile, OS isolation and probe timeout remain on.
Missing envelopes or unsupported cross-tool helper calls are UNKNOWN, never
evidence of no dependency. This measures execute edges, not arbitrary Python
object/data dependencies or resistance to arbitrary interpreter introspection.
"""
import json

from . import sandbox


INSTRUMENT = r'''
_analysis_edges, _analysis_unsupported, _analysis_hits = set(), set(), []
_analysis_wrapped = set()

def _analysis_wrapper(fn, target):
    def instrumented(*args, **kwargs):
        src = _importer()
        _permit(target, src)
        if src is not None and src != target:
            _analysis_edges.add((src, target))
        if (src, target) == _analysis_ablation:
            _analysis_hits.append((src, target))
            return args[0] if args else kwargs['table']
        return fn(*args, **kwargs)
    return instrumented

def _analysis_wrap_loaded():
    for name, module in list(sys.modules.items()):
        if not name.startswith('tools.') or module is None:
            continue
        tid = name.split('.')[1]
        fn = getattr(module, 'execute', None)
        if not callable(fn) or id(fn) in _analysis_wrapped:
            continue
        instrumented = _analysis_wrapper(fn, tid)
        _analysis_wrapped.add(id(instrumented))
        module.execute = instrumented
'''


def worker(ablation=None):
    if ablation is not None and (len(ablation) != 2 or any(not sandbox.TOOL_ID.fullmatch(t) for t in ablation)):
        raise ValueError('ablation must name a valid importer/dependency pair')
    text = sandbox._WORKER

    def replace(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise RuntimeError('analysis worker anchor drift: update and revalidate instrumentation')
        text = text.replace(old, new)

    replace('def _checked_import(name,',
            '_analysis_ablation = ' + repr(tuple(ablation) if ablation else None) + '\n' + INSTRUMENT + '\ndef _checked_import(name,')
    replace('    return _original_import(name, globals, locals, fromlist, level)',
            '    result = _original_import(name, globals, locals, fromlist, level)\n'
            '    _analysis_wrap_loaded()\n    return result')
    replace('    return _original_import_module(name, package)',
            '    result = _original_import_module(name, package)\n'
            '    _analysis_wrap_loaded()\n    return result')
    replace('                        break\n                    caller = caller.f_back',
            "                        if src != target and frame.f_code.co_name != '<module>':\n"
            "                            if frame.f_code.co_name == 'execute':\n"
            '                                _analysis_edges.add((src, target))\n'
            '                            else:\n'
            '                                _analysis_unsupported.add((src, target))\n'
            '                        break\n                    caller = caller.f_back')
    replace('encoded = json.dumps(out).encode()',
            "out = [{'analysis_protocol': 1, 'value': y, 'edges': sorted(_analysis_edges),\n"
            "        'unsupported': sorted(_analysis_unsupported), 'ablation_hits': len(_analysis_hits)} for y in out]\n"
            'encoded = json.dumps(out).encode()')
    return text


def execute(library, tool_id, calls, timeout_s=5.0, ablation=None, *, stop_on_anomaly=False):
    def check(value):
        if stop_on_anomaly and sandbox.is_error(value):
            from .smoke_policy import SmokeStop, ordinary_model_code_error
            if not ordinary_model_code_error(value['__error__']):
                raise SmokeStop('analysis_probe_execution_error')

    rows = sandbox.run_tool(str(library), tool_id, calls, timeout_s, worker_source=worker(ablation))
    normalized = []
    for row in rows:
        if not isinstance(row, dict) or row.get('analysis_protocol') != 1:
            check(row)
            normalized.append({'value': row, 'trace_complete': False, 'edges': [],
                               'unsupported': [], 'ablation_hits': 0})
        else:
            check(row['value'])
            normalized.append(dict(row, trace_complete=not bool(row['unsupported'])))
    if ablation is None:
        # Independent ordinary worker is the authoritative measurement. Trace
        # instrumentation must not silently change a generated tool's behavior.
        baseline = sandbox.run_tool(str(library), tool_id, calls, timeout_s)
        for row, value in zip(normalized, baseline):
            check(value)
            same = json.dumps(row['value'], sort_keys=True) == json.dumps(value, sort_keys=True)
            row['instrumentation_matches_original'] = same
            row['trace_complete'] = row['trace_complete'] and same
            if not same:
                row['instrumented_value'] = row['value']
            row['value'] = value
    return normalized
