"""Service for interacting with the SerpApi search API."""

from typing import Any, Dict, Optional

import httpx

from app.core.config import settings


class SerpApiService:
    """Provides a small wrapper around the SerpApi HTTP API."""

    BASE_URL = "https://serpapi.com/search.json"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or settings.serpapi_api_key

    def search(
        self,
        query: str,
        search_engine: str = "google",
        **params: Any,
    ) -> Dict[str, Any]:
        """Execute a search through SerpApi."""

        if not self.api_key:
            raise ValueError(
                "SerpApi API key is not configured."
            )

        if not query or not query.strip():
            raise ValueError(
                "Search query must not be empty."
            )

        request_params = {
            "engine": search_engine,
            "q": query.strip(),
            "api_key": self.api_key,
        }

        request_params.update(params)

        response = httpx.get(
            self.BASE_URL,
            params=request_params,
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()


serpapi_service = SerpApiService()