"""Build prompt, identical for every arm except the exemplar block.

One template for all arms (fixes the audit's code-path asymmetry: no arm gets
an extra "combine tools" question, a role prior, or a global summary).
"""
import re

from .env_adapter import CONTRACT
from .primitive_contract import render_public_contract
from .target_contract import VERSION as TARGET_VERSION, parse_params

SYSTEM = (
    "You are one agent in a society that builds small Python tools for table "
    "transforms. Each round you write exactly one new tool. " + CONTRACT + " "
    "You may import any listed tool with `from tools import <tool_id>` and call "
    "`<tool_id>.execute(...)`. Standard library only. "
    "TARGET names a task only if execute(table, lookup), with no keyword arguments, "
    "implements that task's entire listed pipeline using its specified parameters. "
    "A reusable primitive or partial pipeline that does not solve an entire task "
    "must use TARGET: NONE. IMPLEMENTS lists only complete primitives that work "
    "with their parameters supplied as keyword arguments. Public feedback and "
    "behaviour probes call without keyword arguments; primitive verification "
    "supplies parameters. Describe required parameters in DESCRIPTION.\n\n"
    + render_public_contract()
)

FORMAT = (
    "Answer in exactly this format:\n"
    "TOOL_LABEL: <short name>\n"
    "TARGET: <NONE if any keyword parameter is required; otherwise an exact task id whose whole pipeline works with no kwargs>\n"
    "IMPLEMENTS: <comma-separated primitive names this tool implements on its own, or NONE>\n"
    "DESCRIPTION: <one line>\n"
    "```python\n<code defining execute(table, lookup, **params)>\n```\n"
    "Before answering, check the TARGET contract: if your code needs a value such "
    "as params['col'] or params['factor'] and has no default, TARGET must be NONE, "
    "even when a menu task uses that primitive. Do not claim a task based only on "
    "its name or one matching step. Do not include this check in the answer."
)

# Explicit opt-in: keep old prompts available for legacy replay and protocols.
PARAM_SYSTEM = (
    "You are one agent in a society that builds small Python tools for table "
    "transforms. Each round you write exactly one new tool. " + CONTRACT + " "
    "You may import any listed tool with `from tools import <tool_id>` and call "
    "`<tool_id>.execute(...)`. Standard library only. "
    "Build a useful reusable component or a complete task pipeline. When your "
    "tool can solve an entire task in the menu, declare that task as TARGET and "
    "the exact JSON keyword arguments as TARGET_PARAMS. We will test "
    "execute(table, lookup, **TARGET_PARAMS) against the ENTIRE task, not just "
    "one matching step. A parameterized primitive can target a matching one-step "
    "task; a multi-step target must implement every step in order. Use {} for "
    "a task implemented with defaults. Otherwise use TARGET: NONE and "
    "TARGET_PARAMS: {}. Do not invent a target or claim a partial pipeline as "
    "a complete task. Reuse is permitted but not required. "
    "IMPLEMENTS lists only complete primitives that work with their public "
    "keyword parameters. Target testing does not establish general primitive "
    "correctness. Public execution feedback uses your declared task parameters "
    "when the contract is valid; unparameterized behaviour probes and independent "
    "primitive verification are separate. Describe required parameters in DESCRIPTION.\n\n"
    + render_public_contract()
)
PARAM_FORMAT = (
    "Answer in exactly this format:\n"
    "TOOL_LABEL: <short name>\n"
    "TARGET: <exact menu task id, or NONE>\n"
    "TARGET_PARAMS: <one-line JSON object of keyword values, or {}>\n"
    "IMPLEMENTS: <complete primitive names, comma-separated, or NONE>\n"
    "DESCRIPTION: <one line describing the interface and capability>\n"
    "```python\n<code defining execute(table, lookup, **params)>\n```\n"
    "Check that your declared invocation implements the whole TARGET pipeline "
    "with its specified parameters. Do not include this check in the answer."
)


def build_user_prompt(round_num, task_specs, catalogue, block, feedback=None, *, target_contract=None):
    lines = [f"Round {round_num}.", ""]
    if feedback:
        lines += [f"Execution of your previous tool {feedback['tool_id']} on a public example input: "
                  f"{feedback['text']}", ""]
    lines += ["Tasks you may target:"]
    for t in task_specs:
        lines.append(f"TASK {t['id']}: {t['spec']}")
    lines += ["", "Tools currently in the library:"]
    if catalogue:
        for e in sorted(catalogue, key=lambda e: e["id"]):
            lines.append(f"- {e['id']} (agent {e['author']:02d}): {e['description']}")
    else:
        lines.append("- (none yet)")
    if block:
        lines += ["", block]
    lines += ["", PARAM_FORMAT if target_contract == TARGET_VERSION else FORMAT]
    return "\n".join(lines)


_FIELDS = ("TOOL_LABEL", "TARGET", "IMPLEMENTS", "DESCRIPTION")
_FIELD = {k: re.compile(rf"^{k}:\s*(.+)$", re.M) for k in _FIELDS}
_CODE = re.compile(r"```python\s*\n(.*?)```", re.S)


def parse_response(text, primitives=(), *, target_contract=None):
    if target_contract == TARGET_VERSION:
        metadata = text.split('```', 1)[0].replace('\r\n', '\n')
        out = {k.lower(): (m.group(1).strip() if (m := re.search(rf'^{k}:[ \t]*([^\r\n]*)$', metadata, re.M)) else None)
               for k in _FIELDS}
    else:
        out = {k.lower(): (m.group(1).strip() if (m := rx.search(text)) else None)
               for k, rx in _FIELD.items()}
    if out["target"] and out["target"].upper() == "NONE":
        out["target"] = None
    impl = out["implements"] or ""
    out["implements"] = [p.strip() for p in impl.split(",")
                         if p.strip() and p.strip().upper() != "NONE"]
    out["implements_unknown"] = [p for p in out["implements"] if p not in primitives]
    code = _CODE.search(text)
    out["source"] = code.group(1) if code else None
    out["parse_ok"] = bool(out["source"] and "def execute" in out["source"])
    if target_contract == TARGET_VERSION:
        # Only metadata before the code fence can declare a task invocation.
        header = metadata
        fields = re.findall(r'^TARGET_PARAMS:[ \t]*(.*)$', header, re.M)
        params, error = ({}, None)
        if len(fields) == 1:
            params, error = parse_params(fields[0])
        else:
            error = 'missing_or_duplicate_target_params'
        if out['target'] is None and params:
            error = 'params_without_target'
        if (len(re.findall(r'^TARGET:', header, re.M)) != 1
                or (not out['target'] and not re.search(r'^TARGET:[ \t]*NONE[ \t]*$', header, re.M | re.I))):
            error = 'missing_or_duplicate_target'
        out.update(target_params=params, target_contract_version=TARGET_VERSION,
                   target_contract_error=error)
    return out
