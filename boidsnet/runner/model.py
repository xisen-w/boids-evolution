"""Model clients.

StubModel is deterministic and makes no network calls; it exists to dry-run
the runner end to end against the mechanism env.  OpenAICompatModel is the
only paid path: it refuses to construct unless spend is explicitly allowed,
and reads the key from an environment variable whose value is never logged.
"""
import inspect
import json
import os
import random
import re
import time


class StubModel:
    """Writes table-pipeline tools from the task menu.  It inlines the env's
    reference primitives (so a 'correct' tool really is correct), drops the
    last step with p=0.3 (bug), and with p=0.35 first calls a listed tool
    (a composition attempt that usually breaks correctness)."""
    name = "stub"

    def __init__(self, seed, env):
        self.rng = random.Random(seed)
        self.tasks = {t["id"]: t["obj"] for t in env.dev_tasks()}
        m = env.m
        self.prelude = "import math\nNUM_COLS = %r\n\n" % (m.NUM_COLS,) + inspect.getsource(m._copy)
        self.src = {n: inspect.getsource(fn) for n, (fn, _, _) in m.PRIMITIVES.items()}
        self.fname = {n: fn.__name__ for n, (fn, _, _) in m.PRIMITIVES.items()}
        by_fname = {v: k for k, v in self.fname.items()}
        # primitives whose reference calls another primitive (e.g. top_k -> sort)
        self.deps = {n: [by_fname[f] for f in re.findall(r"\b(p_\w+)\(", src)
                         if f in by_fname and by_fname[f] != n]
                     for n, src in self.src.items()}

    def complete(self, system, user, temperature, max_tokens):
        ids = re.findall(r"^TASK (\S+):", user, re.M)
        tools = re.findall(r"^- (a\d\d_r\d\d) ", user, re.M)
        tid = self.rng.choice(ids)
        steps = list(self.tasks[tid].steps)
        if self.rng.random() < 0.3 and len(steps) > 1:
            steps = steps[:-1]
        names = sorted({n for n, _ in steps} | {d for n, _ in steps for d in self.deps.get(n, [])})
        header, body = [], []
        if tools and self.rng.random() < 0.35:
            dep = self.rng.choice(tools)
            header.append(f"from tools import {dep}")
            body.append(f"    table = {dep}.execute(table, lookup)")
        for n, params in steps:
            body.append(f"    table = {self.fname[n]}(table, lookup, **{params!r})")
        code = ("from __future__ import annotations\n" + "\n".join(header) + "\n" + self.prelude + "\n\n" +
                "\n\n".join(self.src[n] for n in names) +
                "\n\ndef execute(table, lookup, **params):\n" + "\n".join(body) + "\n    return table\n")
        text = (f"TOOL_LABEL: {'_'.join(n for n, _ in steps)}\nTARGET: {tid}\nIMPLEMENTS: NONE\n"
                f"DESCRIPTION: pipeline {' -> '.join(n for n, _ in steps)}\n```python\n{code}```")
        return text, len(system + user) // 4, len(text) // 4


class OpenAICompatModel:
    """Backend interface (all backends): complete(system, user, temperature,
    max_tokens) -> (text, prompt_tokens, completion_tokens); attribute
    last_retries is set per call.  The key is read from an environment
    variable and never stored in config, manifest or logs."""

    def __init__(self, model, key_env, allow_spend, base_url=None, azure_endpoint=None,
                 api_version=None, send_temperature=True, token_param="max_tokens",
                 param_mode="strict"):
        if not allow_spend:
            raise PermissionError("paid model requested without --allow-spend")
        key = os.environ.get(key_env)
        if not key:
            raise PermissionError(f"environment variable {key_env} is not set")
        if azure_endpoint:
            from openai import AzureOpenAI  # lazy: dry runs need no SDK
            # `model` is the Azure DEPLOYMENT name.
            self.client = AzureOpenAI(api_key=key, azure_endpoint=azure_endpoint,
                                      api_version=api_version or "2024-06-01")
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=key, base_url=base_url)
        self.name = model
        # Sampling-parameter handling (msg #76 item 7).  Reasoning deployments
        # typically reject temperature != 1 and `max_tokens` (they want
        # `max_completion_tokens`).  The frozen protocol should set these
        # explicitly; param_mode='strict' (default) then refuses any change at
        # run time, while 'auto' adapts once and records it in
        # self.param_adaptations, which run.py writes to the manifest.
        self.send_temperature = send_temperature
        self.token_param = token_param
        self.param_mode = param_mode
        self.param_adaptations = []

    MAX_ATTEMPTS = 6           # backoff 2, 4, 8, 16, 32 s (+ jitter)

    def _adapt(self, msg):
        """Return True if a rejected sampling parameter was adapted."""
        if self.param_mode != "auto":
            return False
        low = msg.lower()
        if "temperature" in low and self.send_temperature:
            self.send_temperature = False
            self.param_adaptations.append("dropped temperature (deployment rejected it)")
            return True
        if "max_tokens" in low and self.token_param == "max_tokens":
            self.token_param = "max_completion_tokens"
            self.param_adaptations.append("max_tokens -> max_completion_tokens")
            return True
        return False

    def complete(self, system, user, temperature, max_tokens):
        """Transient API errors are retried with exponential backoff; the
        retry count is exposed so the runner can log it.  After MAX_ATTEMPTS
        the error propagates and the society is marked FAILED (run.py)."""
        self.last_retries = 0
        self.last_cached_tokens = None
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                kw = {self.token_param: max_tokens}
                if self.send_temperature:
                    kw["temperature"] = temperature
                r = self.client.chat.completions.create(
                    model=self.name, messages=[{"role": "system", "content": system},
                                               {"role": "user", "content": user}], **kw)
                u = r.usage
                det = getattr(u, "prompt_tokens_details", None)
                self.last_cached_tokens = getattr(det, "cached_tokens", None) if det else None
                return r.choices[0].message.content or "", u.prompt_tokens, u.completion_tokens
            except Exception as e:  # noqa: BLE001 - SDK error types vary by version
                status = getattr(e, "status_code", None)
                if status == 400 and self._adapt(str(e)):
                    continue         # parameter adapted (auto mode); retry at once
                if status is not None and 400 <= status < 500 and status not in (408, 409, 429):
                    raise            # auth / bad request: retrying will not help
                if attempt == self.MAX_ATTEMPTS - 1:
                    raise
                self.last_retries += 1
                time.sleep(2 ** (attempt + 1) + random.random())
