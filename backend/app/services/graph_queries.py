"""Graph query service skeleton."""

from backend.app.services.name_utils import normalize_name_fields


def normalize_response_names(payload):
	return normalize_name_fields(payload)
