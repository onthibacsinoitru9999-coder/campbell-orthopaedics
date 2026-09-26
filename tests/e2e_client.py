"""E2E Test Client for Campbell Orthopaedic Bible Platform.

Supports dual-mode execution:
1. In-process ASGI testing via FastAPI TestClient (fast, isolated, no open port required).
2. Live HTTP server testing via httpx/requests when CAMBELL_BASE_URL is set (e.g. http://localhost:8000).
"""

import os
import sys
import time
from typing import Optional, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import server
from fastapi.testclient import TestClient
import httpx


class E2ETestResponse:
    """Unified response wrapper conforming to requests/httpx/TestClient response interfaces."""

    def __init__(self, raw_response, elapsed_ms: float):
        self._raw = raw_response
        self.status_code = raw_response.status_code
        self.headers = raw_response.headers
        self.content = raw_response.content
        self.elapsed_ms = elapsed_ms

    def json(self) -> Any:
        return self._raw.json()

    @property
    def text(self) -> str:
        return self._raw.text


class E2EClient:
    """Unified test client for opaque-box E2E testing."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.environ.get("CAMBELL_BASE_URL")
        if self.base_url:
            self.base_url = self.base_url.rstrip("/")
            self._http_client = httpx.Client(base_url=self.base_url, timeout=30.0)
            self._mode = "live"
        else:
            self._test_client = TestClient(server.app)
            self._mode = "in-process"

    @property
    def mode(self) -> str:
        return self._mode

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> E2ETestResponse:
        t0 = time.perf_counter()
        if self._mode == "live":
            resp = self._http_client.get(path, params=params, headers=headers)
        else:
            resp = self._test_client.get(path, params=params, headers=headers)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return E2ETestResponse(resp, elapsed_ms)

    def close(self):
        if self._mode == "live" and hasattr(self, "_http_client"):
            self._http_client.close()


# Shared singleton client for test cases
_default_client: Optional[E2EClient] = None

def get_test_client() -> E2EClient:
    global _default_client
    if _default_client is None:
        _default_client = E2EClient()
    return _default_client
