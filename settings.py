"""
Runtime settings manager.
Loads from settings.json (user overrides) with fallback to config.py defaults.
All edits via the UI are written back to settings.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import config

SETTINGS_FILE = Path(__file__).parent / "settings.json"

# ── Schema: (label, config_key, type, description) ───────────────────────────
SCHEMA: list[tuple[str, str, type, str]] = [
    ("Game",                 "GAME",                  str,   "Active game: Rates, Flips, Crafting"),
    ("League — POE1",        "LEAGUE_POE1",           str,   "POE1 league (poe.ninja / GGG)"),
    ("League — POE2",        "LEAGUE_POE2",           str,   "POE2 league"),
    ("Min Profit %",         "MIN_PROFIT_PERCENT",    float, "Minimum spread % to list a flip"),
    ("Min Volume",           "MIN_VOLUME",            int,   "Minimum trade volume to consider"),
    ("Min Buy — POE1 (chaos)", "MIN_BUY_COST_CHAOS",  float, "POE1 flips: skip cheaper than this (chaos)"),
    ("Min Buy — POE2 (exalted)", "MIN_BUY_COST_EXALTED", float, "POE2 flips: skip cheaper than this (exalted)"),
    ("Max Buy — POE1 (chaos)", "MAX_BUY_COST_CHAOS", float, "POE1: hide rates/flips if buy cost (chaos) exceeds this. 0 = unlimited. Default 999999 shows effectively all — lower to filter."),
    ("Max Buy — POE2 (exalted)", "MAX_BUY_COST_EXALTED", float, "POE2: hide rates/flips if buy cost (exalted) exceeds this. 0 = unlimited. Default 999999 shows effectively all — lower to filter."),
    ("Refresh Interval (s)", "AUTO_REFRESH_INTERVAL", int,   "Auto-refresh interval (watch mode)"),
    ("Fetch POE1 Essence exchange", "FETCH_POE1_ESSENCE_EXCHANGE", bool, "POE1 Convert Tricks: extra Essence exchange (many /details). Off = faster, less coverage."),
    ("Fetch POE1 Tattoo overview", "FETCH_POE1_TATTOO_OVERVIEW", bool, "POE1 Convert Tricks: Tattoo exchange overview (colour hints)."),
    ("Fetch full Crafting sweep", "FETCH_CRAFTING_FULL_SWEEP", bool, "Crafting tab: all item categories. Off = empty hotspots/bulk (saves many HTTP calls)."),
    ("Exchange overview only", "EXCHANGE_USE_OVERVIEW_ONLY", bool, "Rates/Flips: build exchange rows from poe.ninja overview only — no /details per line (fast; buy/sell spread shown as ~0%)."),
]

# Runtime overrides dict — starts from config.py defaults
_overrides: dict[str, Any] = {}


def _default(key: str) -> Any:
    return getattr(config, key)


def get(key: str) -> Any:
    """Return current effective value (override > config.py default)."""
    return _overrides.get(key, _default(key))


def active_league() -> str:
    """League for the currently selected game (POE1 vs POE2 use different GGG realms)."""
    g = str(get("GAME")).lower()
    if g == "poe1":
        return str(get("LEAGUE_POE1"))
    return str(get("LEAGUE_POE2"))


def set_value(key: str, value: Any) -> None:
    """Set a runtime override and persist to settings.json."""
    _overrides[key] = value
    _save()


def load() -> None:
    """Load persisted settings from settings.json into _overrides."""
    if not SETTINGS_FILE.exists():
        return
    try:
        raw = SETTINGS_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        # Migrate legacy single LEAGUE → per-game keys
        if "LEAGUE" in data:
            legacy = data.pop("LEAGUE")
            if "LEAGUE_POE1" not in data:
                data["LEAGUE_POE1"] = legacy
            if "LEAGUE_POE2" not in data:
                # POE2 uses realm=poe2 — do not copy POE1 challenge league names
                data["LEAGUE_POE2"] = _default("LEAGUE_POE2")
            SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        migrated = False
        if data.pop("MAX_FLIP_BUDGET_CHAOS", None) is not None:
            migrated = True
        if "MIN_BUY_COST_EXALTED" not in data:
            data["MIN_BUY_COST_EXALTED"] = _default("MIN_BUY_COST_EXALTED")
            migrated = True
        if migrated:
            SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        _overrides.update(data)
    except (json.JSONDecodeError, OSError):
        pass  # corrupt file — silently ignore, use defaults


def _save() -> None:
    """Write current overrides to settings.json."""
    try:
        SETTINGS_FILE.write_text(
            json.dumps(_overrides, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


def all_values() -> list[dict]:
    """Return all settings as a list of dicts for display."""
    rows = []
    for label, key, typ, desc in SCHEMA:
        default = _default(key)
        current = get(key)
        rows.append({
            "label": label,
            "key": key,
            "type": typ.__name__,   # str/int/float — JSON serializable
            "description": desc,
            "default": default,
            "current": current,
            "modified": current != default,
        })
    return rows


def reset(key: str) -> None:
    """Remove override for key, reverting to config.py default."""
    _overrides.pop(key, None)
    _save()


def reset_all() -> None:
    _overrides.clear()
    _save()
