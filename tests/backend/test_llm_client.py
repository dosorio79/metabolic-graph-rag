from __future__ import annotations

from types import SimpleNamespace

from backend.app.rag import llm_client


def test_generate_answer_returns_fallback_when_api_key_missing(monkeypatch):
    monkeypatch.setattr(
        llm_client,
        "get_settings",
        lambda: SimpleNamespace(
            llm_api_base="https://api.openai.com/v1",
            llm_api_key="",
            llm_model="gpt-4o-mini",
            llm_temperature=0.2,
            llm_max_tokens=400,
            llm_timeout_seconds=30,
        ),
    )

    answer = llm_client.generate_answer("How is pyruvate produced?", "context")

    assert "LLM response unavailable." in answer
    assert "missing APP_LLM_API_KEY" in answer


def test_generate_answer_calls_openai_sdk(monkeypatch):
    captures = {}

    monkeypatch.setattr(
        llm_client,
        "get_settings",
        lambda: SimpleNamespace(
            llm_api_base="https://api.openai.com/v1",
            llm_api_key="test-key",
            llm_model="gpt-4o-mini",
            llm_temperature=0.3,
            llm_max_tokens=200,
            llm_timeout_seconds=15,
        ),
    )

    class DummyCompletions:
        def create(self, **kwargs):
            captures["create_kwargs"] = kwargs
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="Grounded answer"))]
            )

    class DummyChat:
        def __init__(self):
            self.completions = DummyCompletions()

    class DummyClient:
        def __init__(self, **kwargs):
            captures["client_kwargs"] = kwargs
            self.chat = DummyChat()

    monkeypatch.setattr(llm_client, "OpenAI", DummyClient)

    answer = llm_client.generate_answer("How is pyruvate produced?", "Sample context")

    assert answer == "Grounded answer"
    assert captures["client_kwargs"]["api_key"] == "test-key"
    assert captures["client_kwargs"]["base_url"] == "https://api.openai.com/v1"
    assert captures["client_kwargs"]["timeout"] == 15
    assert captures["create_kwargs"]["model"] == "gpt-4o-mini"
    assert captures["create_kwargs"]["temperature"] == 0.3
    assert captures["create_kwargs"]["max_tokens"] == 200
    assert captures["create_kwargs"]["messages"][0]["role"] == "system"
    assert captures["create_kwargs"]["messages"][1]["role"] == "user"
