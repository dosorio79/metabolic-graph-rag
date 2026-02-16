"""ETL configuration and environment loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")


@dataclass(frozen=True)
class ETLSettings:
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str | None


def get_settings() -> ETLSettings:
    return ETLSettings(
        neo4j_uri=os.getenv("APP_NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("APP_NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("APP_NEO4J_PASSWORD"),
    )
