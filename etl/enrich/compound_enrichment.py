"""Compound enrichment helpers for KEGG ingestion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from etl.fetch.kegg_api import fetch_kegg_data
from etl.models.kegg_types import RawReactionRecord
from etl.normalize.name_utils import normalize_name


def enrich_compound_names(
	reactions: list[RawReactionRecord],
	*,
	cache_path: str | Path | None = None,
	session: requests.Session | None = None,
) -> list[RawReactionRecord]:
	"""Attach compound names to reaction records.

	Args:
		reactions: Raw reaction records to enrich.
		cache_path: Optional JSON cache file path for compound names.
		session: Optional requests session for connection reuse.

	Returns:
		Updated reaction records with compound names attached.
	"""

	compound_ids = collect_compound_ids(reactions)
	cache = load_compound_cache(cache_path)
	sess = session or requests.Session()

	for compound_id in sorted(compound_ids):
		if compound_id in cache:
			continue
		entry = fetch_kegg_data("get", compound_id, session=sess)
		cache[compound_id] = extract_compound_name(entry)

	save_compound_cache(cache_path, cache)

	for reaction in reactions:
		names: dict[str, str | None] = {}
		for compound in reaction.get("substrates", []):
			name = cache.get(compound["id"])
			compound["name"] = name
			names[compound["id"]] = name
		for compound in reaction.get("products", []):
			name = cache.get(compound["id"])
			compound["name"] = name
			names[compound["id"]] = name
		reaction["compound_names"] = names

	return reactions


def collect_compound_ids(reactions: list[RawReactionRecord]) -> set[str]:
	"""Collect unique compound IDs from reaction substrates and products."""
	compound_ids: set[str] = set()
	for reaction in reactions:
		for compound in reaction.get("substrates", []):
			compound_ids.add(compound["id"])
		for compound in reaction.get("products", []):
			compound_ids.add(compound["id"])
	return compound_ids


def extract_compound_name(entry: str) -> str | None:
	"""Extract the first compound name from a KEGG compound entry."""
	if not entry:
		return None

	name_line = ""
	capture = False
	for line in entry.splitlines():
		if line.startswith("NAME"):
			capture = True
			name_line = line.replace("NAME", "").strip()
			continue
		if capture:
			if line.startswith(" "):
				name_line += " " + line.strip()
			else:
				break

	if not name_line:
		return None

	return normalize_name(name_line.split(";", 1)[0])


def load_compound_cache(cache_path: str | Path | None) -> dict[str, str | None]:
	"""Load compound name cache from disk if configured."""
	if not cache_path:
		return {}
	path = Path(cache_path)
	if not path.exists():
		return {}
	try:
		return json.loads(path.read_text())
	except json.JSONDecodeError:
		return {}


def save_compound_cache(cache_path: str | Path | None, cache: dict[str, Any]) -> None:
	"""Persist compound name cache to disk if configured."""
	if not cache_path:
		return
	path = Path(cache_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(cache, indent=2, sort_keys=True))
