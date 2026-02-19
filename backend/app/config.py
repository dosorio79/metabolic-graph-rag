"""Backend configuration and environment loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
	neo4j_uri: str
	neo4j_user: str
	neo4j_password: str
	api_host: str
	api_port: int
	log_level: str
	llm_api_base: str
	llm_api_key: str
	llm_model: str
	llm_temperature: float
	llm_max_tokens: int
	llm_timeout_seconds: int
	rag_context_max_reactions: int
	rag_context_max_compounds: int
	rag_context_max_enzymes: int


def _get_int_env(*keys: str, default: int) -> int:
	for key in keys:
		raw = os.getenv(key)
		if raw is None:
			continue
		try:
			value = int(raw)
		except ValueError:
			continue
		if value > 0:
			return value
	return default


def _get_float_env(*keys: str, default: float) -> float:
	for key in keys:
		raw = os.getenv(key)
		if raw is None:
			continue
		try:
			return float(raw)
		except ValueError:
			continue
	return default


def get_settings() -> Settings:
	return Settings(
		neo4j_uri=os.getenv("APP_NEO4J_URI", os.getenv("NEO4J_URI", "bolt://localhost:7687")),
		neo4j_user=os.getenv("APP_NEO4J_USER", os.getenv("NEO4J_USER", "neo4j")),
		neo4j_password=os.getenv("APP_NEO4J_PASSWORD", os.getenv("NEO4J_PASSWORD", "neo4j")),
		api_host=os.getenv("APP_API_HOST", os.getenv("API_HOST", "0.0.0.0")),
		api_port=_get_int_env("APP_API_PORT", "API_PORT", default=8000),
		log_level=os.getenv("APP_LOG_LEVEL", os.getenv("LOG_LEVEL", "info")).lower(),
		llm_api_base=os.getenv("APP_LLM_API_BASE", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")),
		llm_api_key=os.getenv("APP_LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")),
		llm_model=os.getenv("APP_LLM_MODEL", "gpt-4o-mini"),
		llm_temperature=_get_float_env("APP_LLM_TEMPERATURE", default=0.2),
		llm_max_tokens=_get_int_env("APP_LLM_MAX_TOKENS", default=400),
		llm_timeout_seconds=_get_int_env("APP_LLM_TIMEOUT_SECONDS", default=30),
		rag_context_max_reactions=_get_int_env(
			"APP_RAG_CONTEXT_MAX_REACTIONS", "RAG_CONTEXT_MAX_REACTIONS", default=8
		),
		rag_context_max_compounds=_get_int_env(
			"APP_RAG_CONTEXT_MAX_COMPOUNDS", "RAG_CONTEXT_MAX_COMPOUNDS", default=8
		),
		rag_context_max_enzymes=_get_int_env(
			"APP_RAG_CONTEXT_MAX_ENZYMES", "RAG_CONTEXT_MAX_ENZYMES", default=12
		),
	)
