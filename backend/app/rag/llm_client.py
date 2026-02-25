"""OpenAI-compatible LLM client for Task 3 RAG responses."""

from __future__ import annotations

from openai import OpenAI

from backend.app.config import get_settings
from backend.app.rag.prompt_registry import SYSTEM_PROMPT, USER_PROMPT, get_prompt_versions


def _build_messages(question: str, context: str) -> list[dict[str, str]]:
    """Build OpenAI-style chat messages from prompt templates."""
    user_prompt = USER_PROMPT.template.format(context=context, question=question.strip())
    return [
        {"role": "system", "content": SYSTEM_PROMPT.template},
        {"role": "user", "content": user_prompt},
    ]


def _fallback_answer(question: str, context: str, reason: str) -> str:
    """Generate deterministic fallback answer when LLM call is unavailable."""
    return (
        "LLM response unavailable. "
        f"Reason: {reason}. "
        f"Question: {question.strip()} | Context length: {len(context)}"
    )


def generate_answer(question: str, context: str) -> str:
    """Generate a grounded answer using the OpenAI Python SDK."""
    settings = get_settings()
    # Keep pipeline deterministic when credentials are not configured.
    if not settings.llm_api_key:
        return _fallback_answer(question, context, "missing APP_LLM_API_KEY")

    messages = _build_messages(question, context)
    try:
        # `base_url` allows OpenAI-compatible providers, not only OpenAI-hosted.
        client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base.rstrip("/"),
            timeout=settings.llm_timeout_seconds,
        )
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
        content = response.choices[0].message.content
        # Normalize SDK output into plain text for downstream API response.
        answer = str(content).strip()
        if answer:
            return answer
    except Exception as exc:
        return _fallback_answer(question, context, f"request failure ({exc.__class__.__name__})")

    return _fallback_answer(question, context, "empty model response")
