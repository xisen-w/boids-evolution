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
                 param_mode="strict", thinking=None, max_attempts=None, before_request=None,
                 after_response=None):
        if not allow_spend:
            raise PermissionError("paid model requested without --allow-spend")
        if model.startswith("deepseek"):
            if (model != "deepseek-flash" or base_url != "https://api.deepseek.com"
                    or azure_endpoint or thinking != "disabled" or param_mode != "strict"
                    or token_param != "max_tokens" or not send_temperature):
                raise ValueError("DeepSeek pilot requires deepseek-flash, official base URL, explicit disabled thinking, temperature and strict max_tokens")
            if key_env != "BOIDS_PARTNER_API_KEY":
                raise PermissionError("DeepSeek experiments only accept the collaborator's BOIDS_PARTNER_API_KEY")
        elif thinking is not None:
            raise ValueError("thinking is configured only for the DeepSeek pilot")
        if max_attempts is not None:
            if not 1 <= max_attempts <= 6:
                raise ValueError("max_attempts must be between 1 and 6")
            self.MAX_ATTEMPTS = max_attempts
        self.thinking, self.base_url = thinking, base_url
        self.before_request, self.after_response = before_request, after_response
        # msg #105.4: belt and braces with run.py's check.  A key may only be
        # loaded where tool code runs under OS isolation.
        from .sandbox import isolation_level
        if os.environ.get("BOIDS_SANDBOX") == "hook-only" or not isolation_level().startswith("os-"):
            raise PermissionError(f"refusing to load a model key: sandbox isolation is {isolation_level()!r}")
        key = os.environ.get(key_env)
        if not key:
            raise PermissionError(f"environment variable {key_env} is not set")
        # msg #134: explicit transport policy.  The SDK's own retries are OFF
        # (max_retries=0) so that complete()'s loop is the ONLY retry layer
        # (MAX_ATTEMPTS, logged per call); each request has a hard timeout.
        # Worst case per call: MAX_ATTEMPTS x REQUEST_TIMEOUT_S + backoff.
        if azure_endpoint:
            if not api_version:
                # msg #131: never leave the API version implicit (the old silent default was 2024-06-01)
                raise ValueError("Azure needs an explicit --azure-api-version")
            from openai import AzureOpenAI  # lazy: dry runs need no SDK
            # `model` is the Azure DEPLOYMENT name.
            self.client = AzureOpenAI(api_key=key, azure_endpoint=azure_endpoint, api_version=api_version,
                                      timeout=self.REQUEST_TIMEOUT_S, max_retries=0)
        else:
            from openai import OpenAI, DefaultHttpxClient
            transport = {}
            if model.startswith("deepseek"):
                # One budget reservation must not silently follow a redirect
                # into additional HTTP requests (or another endpoint).
                transport["http_client"] = DefaultHttpxClient(follow_redirects=False)
            self.client = OpenAI(api_key=key, base_url=base_url, timeout=self.REQUEST_TIMEOUT_S,
                                 max_retries=0, **transport)
        self.api_version = api_version
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
    REQUEST_TIMEOUT_S = 180.0  # per HTTP request; SDK retries disabled (only our loop retries)

    def transport_policy(self):
        """Recorded in every manifest (msg #134 cost/runtime card)."""
        return {"sdk_max_retries": 0, "request_timeout_s": self.REQUEST_TIMEOUT_S,
                "follow_redirects": not self.name.startswith("deepseek"),
                "runner_max_attempts": self.MAX_ATTEMPTS, "backoff_s": "2^attempt + U(0,1)",
                "retried": "429, 408, 409, 5xx, network; not other 4xx",
                "api_version": getattr(self, "api_version", None)}

    def sampling(self):
        return {"temperature_sent": self.send_temperature, "token_param": self.token_param,
                "param_adaptations": self.param_adaptations,
                "thinking": getattr(self, "thinking", None), "base_url": getattr(self, "base_url", None)}

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
        self.last_response_metadata = None
        for attempt in range(self.MAX_ATTEMPTS):
            # Budget refusal is outside the retry handler: no network call,
            # no credential read, and no retry of a local guard failure.
            if getattr(self, "before_request", None):
                self.before_request(system, user, max_tokens, attempt)
            try:
                kw = {self.token_param: max_tokens}
                if self.send_temperature:
                    kw["temperature"] = temperature
                if getattr(self, "thinking", None) is not None:
                    kw["extra_body"] = {"thinking": {"type": self.thinking}}
                r = self.client.chat.completions.create(
                    model=self.name, messages=[{"role": "system", "content": system},
                                               {"role": "user", "content": user}], **kw)
            except Exception as e:  # noqa: BLE001 - SDK error types vary by version
                from openai import APIConnectionError
                from httpx import TransportError
                status = getattr(e, "status_code", None)
                if status == 400 and attempt < self.MAX_ATTEMPTS - 1 and self._adapt(str(e)):
                    continue         # parameter adapted (auto mode); retry at once
                transient = (isinstance(e, (APIConnectionError, TransportError, ConnectionError, TimeoutError))
                             if status is None else status in (408, 409, 429) or 500 <= status < 600)
                if not transient:
                    raise            # local SDK/type/decoding errors are not transport retries
                if attempt == self.MAX_ATTEMPTS - 1:
                    raise
                self.last_retries += 1
                time.sleep(2 ** (attempt + 1) + random.random())
                continue
            # Never resample an already completed response after a local
            # decoding / usage / ledger error. It may already be billed.
            u = r.usage
            if u is None or u.prompt_tokens is None or u.completion_tokens is None:
                raise RuntimeError("provider response omitted usage; stop without resampling")
            det = getattr(u, "prompt_tokens_details", None)
            self.last_cached_tokens = getattr(u, "prompt_cache_hit_tokens", None)
            if self.last_cached_tokens is None:
                self.last_cached_tokens = getattr(det, "cached_tokens", None) if det else None
            choice = r.choices[0]
            self.last_response_metadata = {"model": getattr(r, "model", None),
                                           "finish_reason": getattr(choice, "finish_reason", None),
                                           "response_id": getattr(r, "id", None)}
            if getattr(self, "after_response", None):
                self.after_response(u.prompt_tokens, u.completion_tokens, self.last_cached_tokens,
                                    self.last_response_metadata)
            return choice.message.content or "", u.prompt_tokens, u.completion_tokens
