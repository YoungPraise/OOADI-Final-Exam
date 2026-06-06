"""
core/api_client.py
──────────────────
HTTP client that mirrors DatabaseService's public API exactly.
The UI screens import this instead of DatabaseService — all method
signatures are identical so no screen code changes.

Targets http://localhost:8000 by default (your PC as both server
and client). Change BASE_URL to a remote host to use a real server.
"""

import requests
from typing import Optional

BASE_URL = "http://localhost:8000"

# Timeout for all requests (seconds)
_TIMEOUT = 10


class ApiClient:
    """
    Drop-in replacement for DatabaseService.
    All methods match DatabaseService's signatures and return types.
    """

    def __init__(self, base_url: str = BASE_URL):
        self._base = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    # ── Internal helper ────────────────────────────────────────────────────
    def _get(self, path: str, params: dict = None) -> dict | list:
        url = f"{self._base}{path}"
        try:
            resp = self._session.get(url, params=params, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot reach PhytoMed API at {self._base}\n"
                "Make sure the server is running:\n"
                "  python -m api.server"
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"API error {e.response.status_code}: {e.response.text}")

    # ── Public API (matches DatabaseService) ──────────────────────────────

    def search(
        self,
        query: str,
        top_k: int = 8,
        doc_type: Optional[str] = None,
    ) -> list:
        """Semantic search. Returns list of {score, type, source_id, metadata}."""
        params = {"q": query, "top_k": top_k}
        if doc_type:
            params["type"] = doc_type
        data = self._get("/search", params)
        return data.get("results", [])

    def get_disease(self, disease_id: int) -> Optional[dict]:
        """Full disease dict or None if not found."""
        try:
            return self._get(f"/diseases/{disease_id}")
        except RuntimeError:
            return None

    def get_plant(self, plant_id: int) -> Optional[dict]:
        """Full plant dict or None if not found."""
        try:
            return self._get(f"/plants/{plant_id}")
        except RuntimeError:
            return None

    def get_all_diseases(self) -> list:
        """Returns list of (id, name) tuples."""
        rows = self._get("/diseases")
        return [(r["id"], r["name"]) for r in rows]

    def get_all_plants(self) -> list:
        """Returns list of (id, name, latin_name) tuples."""
        rows = self._get("/plants")
        return [(r["id"], r["name"], r["latin_name"]) for r in rows]

    def autocomplete_diseases(self, text: str, limit: int = 8) -> list:
        """Returns list of (id, name) tuples."""
        rows = self._get("/autocomplete/diseases", {"q": text, "limit": limit})
        return [(r["id"], r["name"]) for r in rows]

    def autocomplete_plants(self, text: str, limit: int = 8) -> list:
        """Returns list of (id, name, latin_name) tuples."""
        rows = self._get("/autocomplete/plants", {"q": text, "limit": limit})
        return [(r["id"], r["name"], r["latin_name"]) for r in rows]

    def get_stats(self) -> dict:
        """Returns {diseases, plants, links}."""
        return self._get("/stats")
