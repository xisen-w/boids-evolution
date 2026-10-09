"""Runs inside isolated grader; inputs contain no expected outputs or references."""

import contextlib
import copy
import importlib
import json
import sys
from pathlib import Path

job = json.loads(Path("/judge/inputs.json").read_text())
results = []
try:
    module = importlib.import_module("published." + job["identity"])
    import_error = None
except BaseException as exc:
    module, import_error = None, f"{type(exc).__name__}: {exc}"[:1000]
for item in job["cases"]:
    rows, lookup, request = (
        copy.deepcopy(item["rows"]),
        copy.deepcopy(item["lookup"]),
        copy.deepcopy(item["request"]),
    )
    before = copy.deepcopy((rows, lookup, request))
    result = dict(
        family=item["family"], index=item["index"], error=import_error, output=None, input_mutated=False
    )
    counts = getattr(sys.modules.get("sitecustomize"), "COUNTS", {})
    before_calls = {edge: data["calls"] for edge, data in counts.items()}
    before_entries = {edge: data.get("service_entries", 0) for edge, data in counts.items()}
    if module is not None:
        try:
            entry = getattr(sys.modules.get("sitecustomize"), "service_entry", None)
            context = entry("published." + job["identity"]) if entry else contextlib.nullcontext()
            with context:
                result["output"] = getattr(module, item["callable"])(rows, lookup, request)
        except BaseException as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"[:1000]
        try:
            result["input_mutated"] = json.dumps(
                (rows, lookup, request), sort_keys=True, allow_nan=False
            ) != json.dumps(before, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError, OverflowError):
            result["input_mutated"] = True
        try:
            encoded = json.dumps(result["output"], allow_nan=False)
            if len(encoded.encode()) > 32768:
                raise ValueError("service output exceeds 32768-byte per-case contract")
        except (TypeError, ValueError, OverflowError) as exc:
            result["output"] = None
            result["error"] = f"non-JSON output: {type(exc).__name__}: {exc}"[:1000]
    result["executed_edges"] = [
        edge for edge, data in counts.items() if data["calls"] > before_calls.get(edge, 0)
    ]
    result["service_entry_edges"] = [
        edge for edge, data in counts.items() if data.get("service_entries", 0) > before_entries.get(edge, 0)
    ]
    results.append(result)
    Path("/trace/outputs.json").write_text(json.dumps(results, allow_nan=False))
if not job["cases"]:
    Path("/trace/outputs.json").write_text("[]")
