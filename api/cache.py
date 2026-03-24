"""
Shared TTL cache + single-flight for the poe.ninja client.

- **TTL**: entries expire after ``ttl`` seconds (per call site).
- **Single-flight**: concurrent ``get_or_compute(..., same key)`` runs the factory once;
  other threads wait and receive the same result (avoids duplicate full-economy fetches).
- **Bound**: store is pruned if it grows past ``MAX_ENTRIES`` (oldest timestamps dropped first).

HTTP GET dedup uses the same store with keys like ``http|https://...|{"league":...}``.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")

_MAX_ENTRIES = 2500

_store: dict[str, tuple[float, Any]] = {}
_guard = threading.Lock()
_locks: dict[str, threading.Lock] = {}


def _lock_for(key: str) -> threading.Lock:
    with _guard:
        if key not in _locks:
            _locks[key] = threading.Lock()
        return _locks[key]


def cache_get(key: str, ttl: float) -> Optional[Any]:
    if ttl <= 0:
        return None
    if key not in _store:
        return None
    ts, data = _store[key]
    if time.time() - ts >= ttl:
        return None
    return data


def cache_set(key: str, data: Any) -> None:
    _store[key] = (time.time(), data)
    if len(_store) > _MAX_ENTRIES:
        _prune_oldest()


def _prune_oldest() -> None:
    """Drop ~oldest half by timestamp to cap memory."""
    n = len(_store)
    if n <= _MAX_ENTRIES:
        return
    keys_by_age = sorted(_store.keys(), key=lambda k: _store[k][0])
    for k in keys_by_age[: max(1, n // 2)]:
        _store.pop(k, None)


def cache_clear() -> None:
    """Clear all entries and per-key locks (call after settings change / user refresh-all)."""
    _store.clear()
    with _guard:
        _locks.clear()


def get_or_compute(key: str, ttl: float, compute: Callable[[], T]) -> T:
    """
    Return cached value if fresh; otherwise run ``compute()`` once per key (single-flight).
    If ``ttl`` <= 0, no cache and no lock (always runs ``compute()``).
    """
    if ttl <= 0:
        return compute()
    hit = cache_get(key, ttl)
    if hit is not None:
        return hit  # type: ignore[return-value]
    lk = _lock_for(key)
    with lk:
        if ttl > 0:
            hit = cache_get(key, ttl)
            if hit is not None:
                return hit  # type: ignore[return-value]
        data = compute()
        if ttl > 0:
            cache_set(key, data)
        return data
