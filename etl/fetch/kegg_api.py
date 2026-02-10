"""Fetch helpers for the KEGG REST API."""

from __future__ import annotations

import time

import requests

BASE_URL = "https://rest.kegg.jp"


def fetch_kegg_data(
    endpoint: str,
    entries: str,
    *,
    timeout: int = 20,
    retries: int = 3,
    session: requests.Session | None = None,
    backoff: float = 1.5,
) -> str:
    """Fetch raw text from a KEGG REST endpoint.

    Args:
        endpoint: KEGG REST endpoint name (e.g., "get", "list").
        entries: Entry id or entry list passed to KEGG.
        timeout: Request timeout in seconds.
        retries: Number of attempts before giving up.
        session: Optional requests session for connection reuse.
        backoff: Multiplier for retry sleep time.

    Returns:
        Raw response text or an empty string on failure.
    """

    # Normalize inputs and build the request URL.
    entries = entries.strip()
    url = f"{BASE_URL}/{endpoint}/{entries}"

    sess = session or requests.Session()

    # Retry transient failures with incremental backoff.
    for attempt in range(1, retries + 1):
        try:
            # Perform the request and return raw response text.
            response = sess.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            if attempt == retries:
                print(f"[KEGG ERROR] {url} -> {e}")
                return ""

            sleep_time = backoff * attempt
            print(f"[KEGG RETRY {attempt}/{retries}] waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)

    return ""
