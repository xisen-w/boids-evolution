import json
import threading
import time
from pathlib import Path

from minisweagent.exceptions import FormatError
from minisweagent.models.litellm_response_model import LitellmResponseModel
from openai import OpenAI

TRANSPORT_TIMEOUT_SECONDS = 180


def normalize_input(items):
    allowed = {
        "message": {"type", "role", "content"},
        "function_call": {"type", "name", "arguments", "call_id"},
        "function_call_output": {"type", "call_id", "output"},
        "reasoning": {"type", "id", "summary", "encrypted_content"},
    }
    return [
        {
            k: v
            for k, v in item.items()
            if v is not None and k in allowed.get(item.get("type", "message"), set(item))
        }
        for item in items
    ]


class Budget:
    def __init__(self, root: Path, call_limit=240, output_limit=500_000):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        if any(root.glob("request-*.json")):
            raise ValueError("budget directory already has requests; use a new run")
        self.call_limit, self.output_limit = call_limit, output_limit
        self.calls = self.output_reserved = 0
        self.lock = threading.Lock()

    def reserve(self, payload, label):
        with self.lock:
            tokens = payload["max_output_tokens"]
            if self.calls >= self.call_limit or self.output_reserved + tokens > self.output_limit:
                raise RuntimeError("hard request/output reservation limit")
            self.calls += 1
            self.output_reserved += tokens
            index = self.calls
            (self.root / f"request-{index:04d}.json").write_text(
                json.dumps(dict(label=label, timestamp=time.time(), payload=payload), indent=2)
            )
            return index

    def save(self, index, result):
        (self.root / f"response-{index:04d}.json").write_text(json.dumps(result, indent=2))


class AgentPortModel(LitellmResponseModel):
    """Pinned mini-SWE-agent protocol; explicit gateway transport without hidden retries."""

    def __init__(self, key: str, budget: Budget, label: str, max_tokens=3000):
        super().__init__(model_name="azure:gpt-6-luna", cost_tracking="ignore_errors")
        self.client = OpenAI(
            api_key=key,
            base_url="https://agentport.world/v1",
            max_retries=0,
            timeout=TRANSPORT_TIMEOUT_SECONDS,
        )
        self.budget, self.label, self.max_tokens = budget, label, max_tokens

    def query(self, messages, **kwargs):
        from minisweagent.models.utils.actions_toolcall_response import BASH_TOOL_RESPONSE_API

        payload = dict(
            model="azure:gpt-6-luna",
            input=normalize_input(self._prepare_messages_for_api(messages)),
            tools=[BASH_TOOL_RESPONSE_API],
            parallel_tool_calls=False,
            max_output_tokens=self.max_tokens,
            reasoning={"effort": "low"},
        )
        index = self.budget.reserve(payload, self.label)
        try:
            response = self.client.responses.create(**payload)
            raw = response.model_dump(mode="json")
            self.budget.save(index, raw)
        except Exception as exc:
            self.budget.save(index, {"error_type": type(exc).__name__, "error": str(exc)[:1000]})
            raise
        if raw.get("model") != "gpt-6-luna":
            raise RuntimeError("provider returned unexpected model")
        try:
            actions = self._parse_actions(response)
        except FormatError as exc:
            exc.messages[0]["extra"].update(response=raw, request_index=index)
            raise
        raw["extra"] = dict(
            actions=actions,
            cost=0.0,
            cost_status="unpriced_not_free",
            usage=raw.get("usage"),
            request_index=index,
            timestamp=time.time(),
        )
        return raw
