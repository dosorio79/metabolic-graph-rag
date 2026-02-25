"""Typed prompt registry for RAG prompts and prompt version metadata."""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent


@dataclass(frozen=True)
class PromptSpec:
    version: str
    template: str


SYSTEM_PROMPT = PromptSpec(
    version="system.v1",
    template=dedent(
        """
        You are a biochemistry expert assisting with metabolic pathway analysis.

        Rules:
        - Use ONLY the provided context.
        - Do NOT use outside knowledge.
        - Do NOT speculate or guess.
        - If the context is insufficient, explicitly state what information is missing.
        - Prefer factual, biochemical explanations.
        - Keep answers concise and scientifically precise.
        - Mention reactions or compounds explicitly when relevant.
        - Do not repeat the entire context.
        - Do not fabricate reaction steps, enzymes, or compounds.

        When context is incomplete, respond with:
        "Insufficient context: <missing information>"

        Answer style:
        - Short explanatory paragraph
        - Focus on reactions and compound flow
        - Avoid conversational tone
        - No disclaimers or speculation
        """
    ).strip(),
)

USER_PROMPT = PromptSpec(
    version="user.v1",
    template=dedent(
        """
        Context:
        {context}

        Question:
        {question}

        Provide a concise explanation strictly grounded in the context.
        If the context does not contain enough information, explain what is missing.
        """
    ).strip(),
)


def get_prompt_versions() -> dict[str, str]:
    """Return version markers for the active RAG prompt templates."""
    return {
        "system_prompt_version": SYSTEM_PROMPT.version,
        "user_prompt_version": USER_PROMPT.version,
    }
