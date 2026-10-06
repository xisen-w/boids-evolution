"""Descriptive diagnostic flags, not significance tests or auto-run permission."""


def summarize(report):
    rows = []
    for result in report['results']:
        s = result.get('mechanism_analysis') or {}
        if not s or 'mechanism_delivery' not in s:
            rows.append({'arm': result['arm'], 'warnings': ['measurement_summary_missing']})
            continue
        delivery, mc = s['mechanism_delivery'], s['M_cross']
        u = s['depth_utility']['pooled_U_dev']
        warnings = []
        if u == 0:
            warnings.append('utility_floor')
        if u == 1:
            warnings.append('utility_ceiling')
        if not delivery['declared_target_passes']:
            warnings.append('no_passing_declared_targets')
        if result['arm'][1] == '1' and not delivery['A_nonfallback_opportunities']:
            warnings.append('alignment_only_fallback_or_no_evidence')
        if result['arm'][0] == '1' and not delivery['S_opportunities']:
            warnings.append('no_separation_opportunity')
        if mc['unknown_tools']:
            warnings.append('M_cross_partially_identified')
        if not s['dependency_edges']:
            warnings.append('no_cross_agent_dependency_candidates')
        if delivery['invalid_target_contracts']:
            warnings.append('invalid_declared_target_contracts')
        rows.append({'arm': result['arm'], 'U_dev': u, 'warnings': warnings,
                     'mechanism_delivery': delivery, 'M_cross': mc})
    return {'status': 'DEVELOPMENT_DIAGNOSTIC_ONLY', 'arms': rows,
            'automatic_next_run': False, 'paper_ready': False,
            'interpretation': 'Warnings request diagnosis, not rerunning until positive. Missing dependencies may be a genuine outcome; unknown is not zero.'}
