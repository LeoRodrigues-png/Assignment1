from __future__ import annotations

import time
from typing import Any

import httpx


class RateCache:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._value: float | None = None
        self._expires_at: float = 0.0

    def get(self) -> float | None:
        if self._value is None:
            return None
        if time.time() >= self._expires_at:
            return None
        return self._value

    def set(self, value: float) -> None:
        self._value = float(value)
        self._expires_at = time.time() + self.ttl_seconds


_usd_to_eur_cache = RateCache(ttl_seconds=300)


async def get_usd_to_eur_rate() -> float:
    cached = _usd_to_eur_cache.get()
    if cached is not None:
        return cached

    # No-auth endpoints are easiest to run in a CI pipeline, so we stick to those.
    url_primary = "https://api.exchangerate.host/latest"
    params_primary = {"base": "USD", "symbols": "EUR"}

    # Fallback in case the primary API is down/rate-limited.
    url_fallback = "https://open.er-api.com/v6/latest/USD"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url_primary, params=params_primary)
            r.raise_for_status()
            data: dict[str, Any] = r.json()
            rate = float(data["rates"]["EUR"])
            _usd_to_eur_cache.set(rate)
            return rate
        except Exception:
            r = await client.get(url_fallback)
            r.raise_for_status()
            data = r.json()
            rate = float(data["rates"]["EUR"])
            _usd_to_eur_cache.set(rate)
            return rate

