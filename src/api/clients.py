"""
API Clients for test automation.

Provides HTTPX-based async API client with automatic authentication
and error handling.
"""

from typing import Any

import httpx
from src.config.settings import settings


class APIClient:
    """
    Async API client with automatic authentication and base URL handling.

    Usage:
        async with APIClient() as client:
            response = await client.get("/users")

    Attributes:
        base_url: Base API URL from settings
        headers: Default headers including auth token
    """

    def __init__(self, base_url: str | None = None, token: str | None = None):
        """
        Initialize API client.

        Args:
            base_url: Override default API base URL
            token: Override default API token
        """
        self.base_url = base_url or settings.effective_api_url
        self.token = token or settings.api_token
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        """Get default headers with authentication."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def __aenter__(self) -> "APIClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=settings.timeout / 1000,
        )
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """
        Make GET request.

        Args:
            path: Request path
            params: Query parameters

        Returns:
            httpx.Response object

        Raises:
            httpx.HTTPStatusError: On HTTP error status codes
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return await self._client.get(path, params=params)

    async def post(
        self, path: str, json: dict[str, Any] | None = None
    ) -> httpx.Response:
        """
        Make POST request.

        Args:
            path: Request path
            json: JSON body

        Returns:
            httpx.Response object
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return await self._client.post(path, json=json)

    async def put(
        self, path: str, json: dict[str, Any] | None = None
    ) -> httpx.Response:
        """Make PUT request."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return await self._client.put(path, json=json)

    async def delete(self, path: str) -> httpx.Response:
        """Make DELETE request."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return await self._client.delete(path)
