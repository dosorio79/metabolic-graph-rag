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


def get_settings() -> Settings:
	return Settings(
		neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
		neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
		neo4j_password=os.getenv("NEO4J_PASSWORD", "neo4j"),
	)
