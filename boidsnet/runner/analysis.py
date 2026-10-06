"""Experiments 2–4 on existing societies, zero model calls, no test unsealing.

Run with --society and a NEW --out directory outside that society. Original
sources, frozen selection, responses and scores are hashed and never changed.
All per-probe outputs are retained; bad/missing measurements are not zero
effects. Identity-ablation evidence uses declared DEV targets only.
"""
import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import zlib
from collections import Counter

from . import analysis_worker
from .env_adapter import MechEnv
from .freeze import code_hash
from .library import Library
from .mechanisms import text_pairs
from .run import DEFAULT_ENV
from .sandbox import isolation_level, is_error

ANALYSIS_PROTOCOL = {
    'version': 'sac-analysis-v1', 'model_calls': 0, 'test_unsealed': False,
    'unparameterized_seeds': list(range(40000, 40008)),
    'parameterized_seeds': [list(range(40000 + 8*j, 40008 + 8*j)) for j in range(3)],
    'parameter_rng': 'Random(45000 + crc32(primitive.encode(utf-8)) % 2000); three sequential draws',
    'reliability_seeds': [list(range(45000 + 4*j, 45004 + 4*j)) for j in range(3)],
    'target_and_ablation_seeds': list(range(47000, 47008)),
    'comparison': 'mechenv.tables_equal; ordered rows, exact keys, floats rounded to six decimals',
    'ablation': 'importer-specific execute identity; other importers unchanged',
    'M_cross_denominator': 'all solver-listed frozen tools; dependency-only tools excluded',
    'candidate_edge_scope': 'direct outgoing edges of the evaluated importer, not transitive edges of its dependencies',
    'behavior_denominator': 'unordered tool-pair x shared condition; noargs plus three draws per shared declared primitive',
    'behavior_comparable': 'both tools return valid tables on all eight probes; common errors never duplicates',
    'trace_boundary': 'execute-call dependencies; non-execute cross-tool helpers or missing trace are unknown',
    'trace_validation': 'every intact probe is also run with the ordinary worker; disagreements make trace unknown',
    'nonfinite_serialization': 'raw NaN/Infinity values use __nonfinite_float__ tagged objects in saved JSON; scoring precedes serialization',
}


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    path = Path(path)
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            return {'__nonfinite_float__': str(value)}
        if isinstance(value, dict):
            return {k: finite(v) for k, v in value.items()}
        if isinstance(value, (tuple, list)):
            return [finite(v) for v in value]
        return value
    with path.open('x', encoding='utf-8') as f:
        json.dump(finite(data), f, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        f.write('\n')
    path.chmod(0o600)


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(root).rglob('*')) if p.is_file()}


def parameter_draws(env, primitive):
    rng = random.Random(45000 + zlib.crc32(primitive.encode('utf-8')) % 2000)
    return [env.m.PRIMITIVES[primitive][1](rng) for _ in range(3)]


def calls_for(env, seeds, params=None):
    return [{'args': [env.m.gen_table(s), env.m.gen_lookup(s)], 'kwargs': copy.deepcopy(params or {})} for s in seeds]


def valid_table(value):
    return isinstance(value, list) and all(isinstance(r, dict) and
        all(isinstance(k, str) and (v is None or isinstance(v, (int, float, str))) for k, v in r.items()) for r in value)


def verdict(env, rows, expected):
    if len(rows) != len(expected) or not rows:
        raise ValueError('incomplete probe vector')
    passed = [not is_error(r['value']) and env.m.tables_equal(r['value'], y) for r, y in zip(rows, expected)]
    crashes = sum(is_error(r['value']) for r in rows)
    return {'passed': all(passed), 'n_pass': sum(passed), 'n_total': len(rows), 'crashed': crashes,
            'normal_rate': (len(rows) - crashes) / len(rows),
            'trace_complete': all(r['trace_complete'] for r in rows)}


def reference_outputs(env, calls, fn):
    return [fn(*copy.deepcopy(c['args']), **copy.deepcopy(c['kwargs'])) for c in calls]


def pair_behavior(env, left, right):
    """Neither exceptions nor two equally malformed non-table values match."""
    if len(left) != 8 or len(right) != 8:
        raise ValueError('behavior conditions require eight paired probes')
    comparable = all(valid_table(r['value']) for r in left + right)
    return {'comparable': comparable,
            'duplicate': comparable and all(env.m.tables_equal(a['value'], b['value']) for a, b in zip(left, right))}


def classify_edge(env, intact, ablated, expected, edge):
    base = verdict(env, intact, expected)
    if not base['trace_complete']:
        return 'unknown'
    if not base['passed']:
        return 'intact_failed'
    used = any(list(edge) in r['edges'] or tuple(edge) in r['edges'] for r in intact)
    if not used:
        return 'unused'
    if ablated is None or not all(r['trace_complete'] for r in ablated):
        return 'unknown'
    if not sum(r['ablation_hits'] for r in ablated):
        return 'unknown'  # alias / unsupported execution bypassed the intervention
    changed = verdict(env, ablated, expected)
    if changed['crashed']:
        return 'structural'  # any crash is not clean functional counterfactual evidence
    return 'no_observed_effect' if changed['passed'] else 'functional_load_bearing'


def m_cross_summary(tools, edges):
    numerator = sum(t['status'] == 'functional_load_bearing' for t in tools)
    unknown = sum(t['status'] in ('unknown', 'no_valid_target') for t in tools)
    n = len(tools)
    counts = dict(sorted(Counter(e['classification'] for e in edges).items()))
    classifiable = sum(e['classification'] in ('functional_load_bearing', 'no_observed_effect', 'unused', 'structural') for e in edges)
    return {'numerator': numerator, 'denominator': n, 'unknown_tools': unknown,
            'observed_fraction': numerator / n if n else None,
            'lower_bound': numerator / n if n else None,
            'upper_bound': (numerator + unknown) / n if n else None,
            'status': 'undefined_empty_library' if not n else ('partially_identified' if unknown else 'identified_on_fixed_probes'),
            'tool_status_counts': dict(sorted(Counter(t['status'] for t in tools).items())),
            'edge_counts': counts, 'classifiable_edges': classifiable,
            'load_bearing_edge_fraction': counts.get('functional_load_bearing', 0) / classifiable if classifiable else None}


def direct_cross_edges(tid, index, source, rows=()):
    static = Library.static_imports(None, source)
    candidates = {(tid, d) for d in static if d in index and index[d]['author'] != index[tid]['author']}
    for row in rows:
        candidates.update((src, dest) for src, dest in row['edges'] + row['unsupported']
                          if src == tid and dest in index and index[src]['author'] != index[dest]['author'])
    return candidates


def coverage(index, measurements, ids):
    reliable = {tid: sorted(p for p, v in measurements[tid]['reliability'].items() if v['verdict']['passed']) for tid in ids}
    by_primitive = {}
    for p in measurements[next(iter(measurements))]['primitive_universe'] if measurements else []:
        declared = [tid for tid in ids if p in measurements[tid]['reliability']]
        passing = [tid for tid in declared if p in reliable[tid]]
        by_primitive[p] = {'declared': len(declared), 'reliable': len(passing),
                           'reliability': len(passing) / len(declared) if declared else None}
    union = sorted({p for ps in reliable.values() for p in ps})
    return {'n_tools': len(ids), 'reliable_primitive_count': len(union), 'reliable_primitives': union,
            'per_tool': reliable, 'per_primitive': by_primitive}


def behavior_summary(env, ids, measurements):
    rows = []
    for left, right in itertools.combinations(sorted(ids), 2):
        common = sorted(set(measurements[left]['behavior']) & set(measurements[right]['behavior']))
        for condition in common:
            result = pair_behavior(env, measurements[left]['behavior'][condition]['rows'], measurements[right]['behavior'][condition]['rows'])
            rows.append(dict(left=left, right=right, condition=condition, **result))
    def summarize(selected):
        comparable = sum(r['comparable'] for r in selected)
        duplicates = sum(r['duplicate'] for r in selected)
        return {'candidate_pair_conditions': len(selected), 'comparable_pair_conditions': comparable,
                'duplicate_pair_conditions': duplicates,
                'comparable_fraction': comparable / len(selected) if selected else None,
                'duplicate_fraction_among_comparable': duplicates / comparable if comparable else None}
    return {'overall': summarize(rows), 'noargs': summarize([r for r in rows if r['condition'] == 'noargs']),
            'parameterized': summarize([r for r in rows if r['condition'] != 'noargs']), 'pairs': rows}


def depth_summary(society, env, utility_name='utility_dev'):
    utility = read(society / utility_name / 'utility.json')
    if utility['split'] != 'dev':
        raise ValueError('this offline command audits development artifacts only')
    tasks = {t['id']: t for t in env.dev_tasks()}
    audits = [read(p) for p in sorted((society / utility_name / 'private_audit').glob('task_*.json'))]
    seen = set()
    values = {}
    for a in audits:
        pair = (a['task'], a['attempt'])
        if a['status'] != 'SCORED' or pair in seen or a['task'] not in tasks:
            raise ValueError('missing/duplicate/invalid scored dev artifact')
        expected_pass = bool(a['gate_ok'] and a.get('verdict') and a['verdict']['n_pass'] == a['verdict']['n_total'] == 8)
        if type(a['passed']) is not bool or a['passed'] != expected_pass:
            raise ValueError('stored pass differs from raw gate/verdict')
        seen.add(pair)
        values.setdefault(tasks[a['task']]['depth'], {}).setdefault(a['task'], []).append(int(a['passed']))
    expected = {(tid, k) for tid in utility['task_ids'] for k in range(utility['attempts'])}
    if seen != expected or utility['solver_truncated_by_budget']:
        raise ValueError('incomplete evaluation cannot become a full depth outcome')
    out = {}
    for depth, by_task in sorted(values.items()):
        task_scores = {tid: sum(v) / len(v) for tid, v in sorted(by_task.items())}
        out[str(depth)] = {'U_dev': sum(task_scores.values()) / len(task_scores),
                           'n_tasks': len(task_scores), 'n_attempts': sum(map(len, by_task.values())),
                           'task_scores': task_scores}
    return {'diagnostic_only': True, 'by_depth': out,
            'pooled_U_dev': sum(sum(v) for d in values.values() for v in d.values()) / len(seen)}


def verify_frozen_inputs(society, utility_name, index, freeze):
    """Raw measurements apply to the frozen selection only with identical ACLs."""
    society = Path(society)
    ids = freeze['kept'] + freeze['dependency_only']
    if len(set(ids)) != len(ids) or not set(ids) <= set(index):
        raise ValueError('invalid or overlapping frozen membership')
    raw_acl = read(society / 'library/acl.json')
    frozen_acl = read(society / utility_name / 'frozen_library/acl.json')
    for tid in ids:
        if tid not in raw_acl or frozen_acl.get(tid) != raw_acl[tid]:
            raise ValueError('raw/frozen ACL mismatch; cannot reuse raw measurements')
        if (society / 'library/tools' / (tid + '.py')).read_bytes() != (society / utility_name / 'frozen_library/tools' / (tid + '.py')).read_bytes():
            raise ValueError('raw/frozen source mismatch')


def analyze_society(society, out, env=None, *, require_os=True, utility_name='utility_dev', progress=False,
                    stop_on_smoke_anomaly=False):
    society, out = Path(society).resolve(), Path(out).resolve()
    if society == out or society in out.parents or out in society.parents:
        raise ValueError('analysis output must be separate from original society')
    env = env or MechEnv(DEFAULT_ENV)
    analyzer_hash = code_hash(env.path)
    if require_os and not isolation_level().startswith('os-'):
        raise PermissionError('analysis of generated tools requires OS sandbox isolation')
    original = hashes(society)
    index = read(society / 'library/index.json')
    manifest = read(society / 'run_manifest.json')
    if manifest.get('env_sha256') and manifest['env_sha256'] != env.file_sha256:
        raise ValueError('analysis environment differs from source society')
    freeze = read(society / utility_name / 'frozen_library/freeze.json')
    kept = freeze['kept']
    if len(set(kept)) != len(kept) or not set(kept) <= set(index):
        raise ValueError('invalid frozen tool membership')
    verify_frozen_inputs(society, utility_name, index, freeze)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    def probe(library, tid, calls, **kwargs):
        return analysis_worker.execute(library, tid, calls, stop_on_anomaly=stop_on_smoke_anomaly, **kwargs)
    try:
        measurements = {}
        for tid, entry in sorted(index.items()):
            measure = {'primitive_universe': env.primitives, 'behavior': {}, 'reliability': {},
                       'unknown_primitive_declarations': sorted(set(entry.get('implements', [])) - set(env.primitives))}
            jobs = [('behavior', 'noargs', calls_for(env, ANALYSIS_PROTOCOL['unparameterized_seeds']),
                     {'seeds': ANALYSIS_PROTOCOL['unparameterized_seeds']})]
            for p in sorted(set(entry.get('implements', [])) & set(env.primitives)):
                draws, reliable_calls = parameter_draws(env, p), []
                for j, params in enumerate(draws):
                    seeds = ANALYSIS_PROTOCOL['parameterized_seeds'][j]
                    calls = calls_for(env, seeds, params)
                    jobs.append(('behavior', p + ':' + str(j), calls, {'params': params, 'seeds': seeds}))
                    reliable_calls += calls_for(env, ANALYSIS_PROTOCOL['reliability_seeds'][j], params)
                expected = reference_outputs(env, reliable_calls, env.m.PRIMITIVES[p][0])
                jobs.append(('reliability', p, reliable_calls, {'params': draws, 'expected': expected}))
            flat = [c for _, _, calls, _ in jobs for c in calls]
            rows = probe(society / 'library', tid, flat)
            offset = 0
            for kind, name, calls, meta in jobs:
                batch = rows[offset:offset + len(calls)]
                offset += len(calls)
                measure[kind][name] = dict(meta, rows=batch)
                if kind == 'reliability':
                    measure[kind][name]['verdict'] = verdict(env, batch, meta['expected'])
            measurements[tid] = measure
            write(out / (tid + '.json'), measure)
            if progress:
                print('ANALYZED_TOOL', manifest['arm'], tid, flush=True)

        raw_ids = sorted(index)
        raw_coverage = coverage(index, measurements, raw_ids)
        frozen_coverage = coverage(index, measurements, kept)
        # Empty libraries still expose the full denominator/universe.
        for result in (raw_coverage, frozen_coverage):
            for p in env.primitives:
                result['per_primitive'].setdefault(p, {'declared': 0, 'reliable': 0, 'reliability': None})
            result['primitive_universe_size'] = len(env.primitives)
        curve, new_tools = [], []
        seen_primitives = set()
        rounds = [json.loads(s) for s in (society / 'rounds.jsonl').read_text().splitlines()]
        records = {r['tool_id']: r for r in rounds}
        for rnd in range(1, manifest['n_rounds'] + 1):
            current = sorted(tid for tid in index if index[tid]['round'] == rnd)
            newly = set()
            for tid in current:
                ps = set(raw_coverage['per_tool'][tid])
                # Same-round peers were invisible at creation; compare to round start.
                gain = sorted(ps - seen_primitives)
                new_tools.append({'tool_id': tid, 'round': rnd, 'new_reliable_primitives': gain,
                                  'S_fired': (records.get(tid, {}).get('sac_fired') or {}).get('S'),
                                  'interpretation': 'descriptive_not_causal_mediation'})
                newly.update(ps)
            seen_primitives.update(newly)
            curve.append({'round': rnd, 'reliable_primitive_count': len(seen_primitives),
                          'reliable_primitives': sorted(seen_primitives)})

        tasks = {t['id']: t['obj'] for t in env.dev_tasks()}
        edge_rows, tool_rows, target_traces = [], [], {}
        for tid in kept:
            entry = index[tid]
            source = (society / 'library/tools' / (tid + '.py')).read_text()
            known_cross = direct_cross_edges(tid, index, source)
            target = tasks.get(entry.get('target'))
            if target is None:
                tool_rows.append({'tool_id': tid, 'target': entry.get('target'), 'status': 'no_valid_target'})
                for edge in sorted(known_cross):
                    edge_rows.append({'root_tool': tid, 'importer': edge[0], 'dependency': edge[1], 'classification': 'unknown'})
                continue
            calls = calls_for(env, ANALYSIS_PROTOCOL['target_and_ablation_seeds'])
            expected = reference_outputs(env, calls, target.reference)
            intact = probe(society / utility_name / 'frozen_library', tid, calls)
            base = verdict(env, intact, expected)
            trace = {'intact': intact, 'expected': expected, 'verdict': base, 'ablations': {}}
            candidates = direct_cross_edges(tid, index, source, intact)
            statuses = []
            for edge in sorted(candidates):
                used = any(list(edge) in r['edges'] or tuple(edge) in r['edges'] for r in intact)
                ablated = (probe(society / utility_name / 'frozen_library', tid, calls, ablation=edge)
                           if base['passed'] and base['trace_complete'] and used else None)
                category = classify_edge(env, intact, ablated, expected, edge)
                statuses.append(category)
                edge_rows.append({'root_tool': tid, 'importer': edge[0], 'dependency': edge[1], 'classification': category})
                trace['ablations']['->'.join(edge)] = ablated
            status = ('functional_load_bearing' if 'functional_load_bearing' in statuses else
                      'unknown' if not base['trace_complete'] or 'unknown' in statuses else
                      'intact_failed' if not base['passed'] else 'no_observed_functional_dependency')
            tool_rows.append({'tool_id': tid, 'target': entry['target'], 'status': status, 'intact': base})
            target_traces[tid] = trace
        write(out / 'target_and_ablation_traces.json', target_traces)
        pairs, text_status = text_pairs(list(index.values()))
        summary = {'arm': manifest['arm'], 'seed': manifest['seed'], 'n_agents': manifest['n_agents'],
                   'n_rounds': manifest['n_rounds'], 'raw_coverage': raw_coverage,
                   'frozen_coverage': frozen_coverage,
                   'text_redundancy': {'status': text_status, 'n_pairs': len(pairs),
                                       'mean_cosine': sum(p[0] for p in pairs)/len(pairs) if pairs else None},
                   'raw_behavior': behavior_summary(env, raw_ids, measurements),
                   'frozen_behavior': behavior_summary(env, kept, measurements),
                   'coverage_by_round': curve, 'new_capabilities': new_tools,
                   'M_cross': m_cross_summary(tool_rows, edge_rows), 'dependency_tools': tool_rows,
                   'dependency_edges': edge_rows, 'depth_utility': depth_summary(society, env, utility_name)}
        summary['mechanism_delivery'] = {
            'builder_records': len(rounds),
            'target_none': sum(r.get('target') is None for r in rounds),
            'S_opportunities': sum((r.get('sac_evidence') or {}).get('S') is not None for r in rounds),
            'S_fired': sum(bool((r.get('sac_fired') or {}).get('S')) for r in rounds),
            'A_nonfallback_opportunities': sum(bool((r.get('sac_evidence') or {}).get('A')) and not r['sac_evidence']['A']['fallback'] for r in rounds),
            'A_fallback_opportunities': sum(bool(((r.get('sac_evidence') or {}).get('A') or {}).get('fallback')) for r in rounds),
            'builder_cross_agent_imports': sum(len(r.get('cross_agent_imports') or []) for r in rounds),
        }
        if hashes(society) != original or code_hash(env.path) != analyzer_hash:
            raise RuntimeError('original artifacts or analyzer source changed during analysis')
        result = {'status': 'COMPLETE_OFFLINE_ANALYSIS', 'new_model_calls': 0, 'test_unsealed': False,
                  'protocol': ANALYSIS_PROTOCOL, 'source_society': str(society), 'input_sha256': original,
                  'source_unchanged': True, 'analysis_code_sha256': analyzer_hash,
                  'stop_on_smoke_anomaly': stop_on_smoke_anomaly,
                  'source_run_code_sha256': manifest.get('code_sha256'), 'env_sha256': env.file_sha256,
                  'sandbox': isolation_level(), 'summary': summary}
        write(out / 'analysis.json', result)
        return result
    except BaseException as exc:
        write(out / 'FAILED.json', {'status': 'INCOMPLETE_ANALYSIS', 'error_type': type(exc).__name__,
                                    'new_model_calls': 0, 'original_unchanged': hashes(society) == original})
        raise


def aggregate_analyses(root):
    """Paired SOCIETY summaries; never turns probes/tools into replicates."""
    root = Path(root)
    reports = [read(p) for p in sorted(root.glob('*/analysis.json'))]
    if not reports or any(r['status'] != 'COMPLETE_OFFLINE_ANALYSIS' for r in reports):
        raise ValueError('complete analysis inputs required')
    by_seed = {}
    for r in reports:
        if any(r[k] != reports[0][k] for k in ('protocol', 'env_sha256', 'analysis_code_sha256', 'source_run_code_sha256')):
            raise ValueError('analysis protocol/environment/source mismatch')
        s = r['summary']
        block = by_seed.setdefault(s['seed'], {})
        if s['arm'] in block:
            raise ValueError('duplicate society arm/seed')
        block[s['arm']] = s
    contrasts = []
    for seed, block in sorted(by_seed.items()):
        if set(block) != {'000', '100', '011', '111'}:
            raise ValueError('all four paired societies are required; missing is not zero')
        settings = {(s['n_agents'], s['n_rounds']) for s in block.values()}
        menus = {json.dumps({d: [sorted(v['task_scores']), v['n_attempts']] for d, v in s['depth_utility']['by_depth'].items()}, sort_keys=True) for s in block.values()}
        if len(settings) != 1 or len(menus) != 1:
            raise ValueError('paired societies differ in size or evaluation tasks/attempts')
        for a, b in [('111', '000'), ('111', '011'), ('100', '000')]:
            da, db = block[a]['depth_utility'], block[b]['depth_utility']
            depths = {d: da['by_depth'][d]['U_dev'] - db['by_depth'][d]['U_dev'] for d in ('1', '2', '3')}
            contrasts.append({'seed': seed, 'contrast': a + '-' + b,
                'U_dev_difference': da['pooled_U_dev'] - db['pooled_U_dev'], 'depth_differences': depths,
                'multistep_minus_single_gain': (depths['2'] + depths['3']) / 2 - depths['1'],
                'reliable_coverage_difference': block[a]['frozen_coverage']['reliable_primitive_count'] - block[b]['frozen_coverage']['reliable_primitive_count']})
            for name, getter in {
                'raw_reliable_coverage': lambda s: s['raw_coverage']['reliable_primitive_count'],
                'text_redundancy': lambda s: s['text_redundancy']['mean_cosine'],
                'raw_behavior_duplicates': lambda s: s['raw_behavior']['overall']['duplicate_fraction_among_comparable'],
                'raw_behavior_comparable': lambda s: s['raw_behavior']['overall']['comparable_fraction'],
                'frozen_behavior_duplicates': lambda s: s['frozen_behavior']['overall']['duplicate_fraction_among_comparable'],
            }.items():
                va, vb = getter(block[a]), getter(block[b])
                contrasts[-1][name + '_difference'] = va - vb if va is not None and vb is not None else None
            ma, mb = block[a]['M_cross'], block[b]['M_cross']
            contrasts[-1]['M_cross_difference_bounds'] = (
                [ma['lower_bound'] - mb['upper_bound'], ma['upper_bound'] - mb['lower_bound']]
                if ma['lower_bound'] is not None and mb['lower_bound'] is not None else None)
    result = {'status': 'COMPLETE_DEVELOPMENT_ANALYSIS', 'societies': len(reports),
              'paired_blocks': len(by_seed), 'contrasts': contrasts, 'diagnostic_only': True,
              'inference': 'society is the independent unit; one block has no estimable between-society variance; no significance claim',
              'new_model_calls': 0}
    # Per-society metrics, denominator counts and unknowns remain accessible;
    # pair-conditions/probes are never used as independent sample size.
    result['society_summaries'] = [r['summary'] for r in reports]
    write(root / 'paired_summary.json', result)
    return result


def analyze_run(run, out, *, progress=False):
    run, out = Path(run).resolve(), Path(out).resolve()
    if run == out or run in out.parents or out in run.parents:
        raise ValueError('analysis outputs must be outside the original run')
    pilot = read(run / 'pilot_summary.json')
    if pilot['status'] != 'COMPLETE_DEV_DIAGNOSTIC' or pilot['test_unsealed']:
        raise ValueError('only a completed development run is accepted')
    config = read(run / 'reviewed_config.json')['config']
    paths = [run / f"ENG_{arm}_s{seed}" for seed in config['seeds'] for arm in config['arms']]
    if set(config['arms']) != {'000', '100', '011', '111'} or not all(p.is_dir() for p in paths):
        raise ValueError('all four original societies are required')
    before = hashes(run)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    for path in paths:
        analyze_society(path, out / path.name, progress=progress)
    result = aggregate_analyses(out)
    if hashes(run) != before:
        raise RuntimeError('original run changed')
    write(out / 'run_audit.json', {'status': 'COMPLETE_OFFLINE_ANALYSIS', 'new_model_calls': 0,
                                  'source_run': str(run), 'source_unchanged': True, 'input_sha256': before})
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument('--society')
    target.add_argument('--run', help='complete four-arm development run')
    p.add_argument('--out', required=True)
    a = p.parse_args(argv)
    r = analyze_run(a.run, a.out, progress=True) if a.run else analyze_society(a.society, a.out, progress=True)
    print(json.dumps({'status': r['status'], 'new_model_calls': 0, 'out': a.out}))


if __name__ == '__main__':
    main()
