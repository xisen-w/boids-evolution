import json

import pytest

from ecology import model


def test_transport_allows_slow_response_without_sdk_retries(monkeypatch, tmp_path):
    options = {}

    def client(**kwargs):
        options.update(kwargs)
        return object()

    monkeypatch.setattr(model, "OpenAI", client)
    model.AgentPortModel("offline-test-key", model.Budget(tmp_path / "api"), "fixture")
    assert options["timeout"] == 180
    assert options["max_retries"] == 0
    assert options["base_url"] == "https://agentport.world/v1"


def test_timeout_is_archived_once_without_fallback(monkeypatch, tmp_path):
    calls = []

    class Client:
        responses = None

        def __init__(self, **kwargs):
            self.responses = self

        def create(self, **kwargs):
            calls.append(kwargs["model"])
            raise TimeoutError("offline transport fixture")

    monkeypatch.setattr(model, "OpenAI", Client)
    budget = model.Budget(tmp_path / "api")
    agent = model.AgentPortModel("offline-test-key", budget, "fixture")
    with pytest.raises(TimeoutError, match="offline transport"):
        agent.query([])
    assert calls == ["azure:gpt-6-luna"]
    assert budget.calls == 1
    response = json.loads((tmp_path / "api/response-0001.json").read_text())
    assert response["error_type"] == "TimeoutError"
