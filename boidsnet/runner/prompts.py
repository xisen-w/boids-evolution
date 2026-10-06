"""Build prompt, identical for every arm except the exemplar block.

One template for all arms (fixes the audit's code-path asymmetry: no arm gets
an extra "combine tools" question, a role prior, or a global summary).
"""
import re

from .env_adapter import CONTRACT
from .primitive_contract import render_public_contract

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


def build_user_prompt(round_num, task_specs, catalogue, block, feedback=None):
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
    lines += ["", FORMAT]
    return "\n".join(lines)


_FIELDS = ("TOOL_LABEL", "TARGET", "IMPLEMENTS", "DESCRIPTION")
_FIELD = {k: re.compile(rf"^{k}:\s*(.+)$", re.M) for k in _FIELDS}
_CODE = re.compile(r"```python\s*\n(.*?)```", re.S)


def parse_response(text, primitives=()):
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
    return out
