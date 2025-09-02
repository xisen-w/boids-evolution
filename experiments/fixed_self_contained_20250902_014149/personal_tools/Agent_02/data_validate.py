def execute(parameters, context=None):
    """Validate dataset against schema rules."""
    try:
        data = parameters.get('data')
        schema = parameters.get('schema', {})
        report = {"errors": [], "warnings": [], "info": []}
        for idx, row in enumerate(data):
            for field, rules in schema.items():
                value = row.get(field)
                # Check required fields
                if rules.get('required') and value is None:
                    report["errors"].append(f"Row {idx}: Missing {field}")
                # Type check
                expected_type = rules.get('type')
                if value is not None and expected_type:
                    if not isinstance(value, expected_type):
                        report["errors"].append(f"Row {idx}: {field} expected {expected_type.__name__}")
                # Range check
                min_val = rules.get('min')
                max_val = rules.get('max')
                if isinstance(value, (int, float)):
                    if min_val is not None and value < min_val:
                        report["warnings"].append(f"Row {idx}: {field} below min {min_val}")
                    if max_val is not None and value > max_val:
                        report["warnings"].append(f"Row {idx}: {field} above max {max_val}")
        return {"report": report}
    except Exception as e:
        return {"error": str(e)}