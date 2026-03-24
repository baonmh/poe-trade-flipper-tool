"""
poe.ninja API Client for POE2 currency and item data.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from typing import Any, Iterator, List, Optional

import requests

import config
import settings as cfg
from api.cache import cache_clear, cache_set, get_or_compute


def _exchange_overview_only() -> bool:
    """When True, exchange categories skip per-line /details (faster; spreads approximate ~0%)."""
    return bool(cfg.get("EXCHANGE_USE_OVERVIEW_ONLY"))

# Game-specific currency endpoints (the legacy /api/data/currencyoverview ignores ?game=).
_NINJA_ORIGIN = "https://poe.ninja"
POE1_STASH_CURRENCY_URL = f"{_NINJA_ORIGIN}/poe1/api/economy/stash/current/currency/overview"
POE1_STASH_ITEM_URL = f"{_NINJA_ORIGIN}/poe1/api/economy/stash/current/item/overview"
POE1_EXCHANGE_OVERVIEW_URL = f"{_NINJA_ORIGIN}/poe1/api/economy/exchange/current/overview"
POE1_EXCHANGE_DETAILS_URL = f"{_NINJA_ORIGIN}/poe1/api/economy/exchange/current/details"
POE2_EXCHANGE_OVERVIEW_URL = f"{_NINJA_ORIGIN}/poe2/api/economy/exchange/current/overview"
POE2_EXCHANGE_DETAILS_URL = f"{_NINJA_ORIGIN}/poe2/api/economy/exchange/current/details"


def _cache_ttl() -> float:
    return float(getattr(config, "POE_NINJA_CACHE_TTL_SEC", 240) or 240)


def _http_cache_ttl() -> float:
    return float(getattr(config, "POE_NINJA_HTTP_CACHE_TTL_SEC", 0) or 0)


@dataclass
class CurrencyRate:
    name: str
    chaos_equivalent: float
    # poe.ninja encoding:
    #   pay_value   = units-of-this-currency per 1 Chaos (inverted!)
    #   receive_value = Chaos per 1 unit of this currency (direct)
    pay_value: float          # units per chaos  (0 = no buy listings)
    receive_value: float      # chaos per unit   (0 = no sell listings)
    pay_count: int            # trade volume (buy side)
    receive_count: int        # trade volume (sell side)
    pay_listings: int
    receive_listings: int
    # POE2: chaos / divine / exalted ids present in exchange details pairs (trusted routing).
    anchors: frozenset[str] = field(default_factory=frozenset)
    category: str = ""
    icon: str = ""

    @property
    def buy_cost_chaos(self) -> float:
        """Chaos you must spend to BUY 1 unit (= 1/pay_value)."""
        if self.pay_value <= 0:
            return 0.0
        return 1.0 / self.pay_value

    @property
    def sell_price_chaos(self) -> float:
        """Chaos you receive when SELLING 1 unit (= receive_value directly)."""
        return self.receive_value

    @property
    def spread_percent(self) -> float:
        """Spread between sell price and buy cost, as % of buy cost."""
        buy = self.buy_cost_chaos
        sell = self.sell_price_chaos
        if buy <= 0 or sell <= 0:
            return 0.0
        return (sell - buy) / buy * 100

    @property
    def volume(self) -> int:
        return self.pay_count + self.receive_count

    @property
    def listings(self) -> int:
        return self.pay_listings + self.receive_listings


@dataclass
class ItemPrice:
    name: str
    chaos_value: float
    divine_value: float
    exalted_value: float
    count: int              # trade volume
    listing_count: int
    item_type: str = ""
    icon: str = ""

    @property
    def volume(self) -> int:
        return self.count


@dataclass
class FlipOpportunity:
    buy_currency: str
    sell_currency: str
    buy_price_chaos: float      # chaos cost to buy 1 unit of buy_currency
    sell_price_chaos: float     # chaos received when selling 1 unit of buy_currency
    profit_per_unit: float      # chaos profit per unit
    profit_percent: float
    volume: int
    note: str = ""


def _http_get_json(url: str, params: dict) -> Optional[dict]:
    """GET with retries; 429 uses exponential backoff (poe.ninja rate limits parallel bursts)."""
    backoff = 2.0
    max_attempts = 8
    for attempt in range(max_attempts):
        try:
            resp = requests.get(url, params=params, timeout=35, headers={
                "User-Agent": "POE-Trade-Flipping/1.0",
            })
            if resp.status_code == 429:
                if attempt < max_attempts - 1:
                    ra = resp.headers.get("Retry-After")
                    try:
                        wait = float(ra) if ra else backoff
                    except ValueError:
                        wait = backoff
                    wait = min(max(wait, 1.0) + random.uniform(0, 0.75), 120.0)
                    time.sleep(wait)
                    backoff = min(backoff * 1.6, 90.0)
                    continue
            # Missing detail rows (stale overview ids) — skip quietly, no console spam.
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_attempts - 1:
                time.sleep(backoff + random.uniform(0, 0.5))
                backoff = min(backoff * 1.5, 60.0)
                continue
            print(f"[API Error] {e}")
            return None
    return None


def _request(url: str, params: dict) -> Optional[dict]:
    """GET JSON; optional short TTL dedupes identical URLs (see POE_NINJA_HTTP_CACHE_TTL_SEC)."""
    ttl = _http_cache_ttl()
    if ttl <= 0:
        return _http_get_json(url, params)
    key = f"http|{url}|{json.dumps(params, sort_keys=True)}"
    return get_or_compute(key, ttl, lambda: _http_get_json(url, params))


def _detail_delay() -> None:
    """Space out exchange /details calls to reduce 429s."""
    d = float(getattr(config, "POE_NINJA_DETAIL_DELAY_SEC", 0.12) or 0.0)
    if d > 0:
        time.sleep(d)


def _category_pause() -> None:
    """Pause between exchange categories (Currency → next …)."""
    d = float(getattr(config, "POE_NINJA_CATEGORY_PAUSE_SEC", 0.9) or 0.0)
    if d > 0:
        time.sleep(d)


def _normalize_icon_url(raw: Optional[str]) -> str:
    """poe.ninja sometimes returns relative CDN paths; normalize to absolute HTTPS."""
    s = (raw or "").strip()
    if not s:
        return ""
    if s.startswith("http://") or s.startswith("https://"):
        return s
    if s.startswith("//"):
        return "https:" + s
    if s.startswith("/"):
        return "https://web.poecdn.com" + s
    return s


def _parse_stash_currency_lines(data: dict, category: str = "") -> list[CurrencyRate]:
    """Parse POE1 stash-style currencyoverview JSON (pay/receive, chaosEquivalent)."""
    rates: list[CurrencyRate] = []
    for line in data.get("lines") or []:
        pay = line.get("pay") or {}
        recv = line.get("receive") or {}
        pv = float(pay.get("value") or 0.0)
        rv = float(recv.get("value") or 0.0)
        anchors = frozenset({"chaos"}) if pv > 0 and rv > 0 else frozenset()
        rates.append(CurrencyRate(
            name=line.get("currencyTypeName", "Unknown"),
            chaos_equivalent=line.get("chaosEquivalent", 0.0),
            pay_value=pv,
            receive_value=rv,
            pay_count=pay.get("count", 0),
            receive_count=recv.get("count", 0),
            pay_listings=pay.get("listing_count", 0),
            receive_listings=recv.get("listing_count", 0),
            anchors=anchors,
            category=category,
            icon=_normalize_icon_url(line.get("icon")),
        ))
    rates.sort(key=lambda r: r.chaos_equivalent, reverse=True)
    return rates


def _parse_stash_item_lines(data: dict, category: str) -> list[CurrencyRate]:
    """POE1 stash item overview (chaosValue, no pay/receive spread)."""
    rates: list[CurrencyRate] = []
    for line in data.get("lines") or []:
        cv = float(line.get("chaosValue") or 0.0)
        if cv <= 0:
            continue
        vol = int(line.get("count") or 0)
        lst = int(line.get("listingCount") or 0)
        half = vol // 2 if vol else 0
        rates.append(CurrencyRate(
            name=line.get("name", "Unknown"),
            chaos_equivalent=cv,
            pay_value=1.0 / cv,
            receive_value=cv,
            pay_count=half,
            receive_count=vol - half,
            pay_listings=max(1, lst // 2) if lst else 1,
            receive_listings=max(1, lst - lst // 2) if lst else 1,
            anchors=frozenset({"chaos"}),
            category=category,
            icon=_normalize_icon_url(line.get("icon")),
        ))
    rates.sort(key=lambda r: r.chaos_equivalent, reverse=True)
    return rates


def _chaos_equivalent_from_pairs(pairs: list[dict[str, Any]], core: dict[str, Any], game: str) -> float:
    """Chaos per 1 unit from exchange detail pairs + overview core.rates (POE1 vs POE2 rate keys differ)."""
    pmap = {p.get("id"): float(p.get("rate") or 0.0) for p in pairs if p.get("id")}
    rates = core.get("rates") or {}
    g = (game or "poe2").lower()
    chaos_per_divine = 0.0
    chaos_per_exalted = 0.0
    if g == "poe2":
        chaos_per_divine = float(rates.get("chaos") or 0.0)
        rex = float(rates.get("exalted") or 0.0)
        chaos_per_exalted = (chaos_per_divine / rex) if rex > 0 and chaos_per_divine > 0 else 0.0
    else:
        d_per_c = float(rates.get("divine") or 0.0)
        chaos_per_divine = (1.0 / d_per_c) if d_per_c > 0 else 0.0

    if pmap.get("chaos"):
        return pmap["chaos"]
    if pmap.get("divine") and chaos_per_divine > 0:
        return pmap["divine"] * chaos_per_divine
    if pmap.get("exalted") and chaos_per_exalted > 0:
        return pmap["exalted"] * chaos_per_exalted
    return 0.0


# Overview row vs detail pairs can disagree slightly; use as buy/sell band when within this ratio.
_LINE_DETAIL_MAX_SPREAD = 1.30


def _overview_line_chaos_hint(line: dict[str, Any], core: dict[str, Any], game: str) -> float:
    """Snapshot chaos implied by the overview row (chaos / divine / exalted primary)."""
    rates = core.get("rates") or {}
    pv = float(line.get("primaryValue") or 0.0)
    if pv <= 0:
        return 0.0
    mvc = line.get("maxVolumeCurrency")
    g = (game or "poe2").lower()
    if g == "poe2":
        chaos_per_divine = float(rates.get("chaos") or 0.0)
        rex = float(rates.get("exalted") or 0.0)
        chaos_per_exalted = (chaos_per_divine / rex) if rex > 0 and chaos_per_divine > 0 else 0.0
        if mvc == "chaos":
            return pv
        if mvc == "divine" and chaos_per_divine > 0:
            return pv * chaos_per_divine
        if mvc == "exalted" and chaos_per_exalted > 0:
            return pv * chaos_per_exalted
        return 0.0
    d_per_c = float(rates.get("divine") or 0.0)
    chaos_per_divine = (1.0 / d_per_c) if d_per_c > 0 else 0.0
    if mvc == "chaos":
        return pv
    if mvc == "divine" and chaos_per_divine > 0:
        return pv * chaos_per_divine
    return 0.0


def _build_rate_from_overview_only(
    line: dict[str, Any],
    meta: dict[str, Any],
    core: dict[str, Any],
    game: str,
    category: str,
) -> Optional[CurrencyRate]:
    """Single mid-price from overview row — no /details; buy≈sell so spread ~0%."""
    ce = _overview_line_chaos_hint(line, core, game)
    if ce <= 0:
        return None
    buy = sell = ce
    pv_pay = (1.0 / buy) if buy > 0 else 0.0
    recv_v = sell
    if pv_pay <= 0 or recv_v <= 0:
        return None
    name = meta.get("name") or "Unknown"
    icon_raw = meta.get("icon")
    vol = int(float(line.get("volumePrimaryValue") or 0))
    half = vol // 2
    mvc = line.get("maxVolumeCurrency")
    anchors = (
        frozenset({mvc})
        if mvc in ("chaos", "divine", "exalted")
        else frozenset({"chaos"})
    )
    return CurrencyRate(
        name=name,
        chaos_equivalent=ce,
        pay_value=pv_pay,
        receive_value=recv_v,
        pay_count=half,
        receive_count=max(0, vol - half),
        pay_listings=max(1, half) if anchors else 0,
        receive_listings=max(1, vol - half) if anchors else 0,
        anchors=anchors,
        category=category,
        icon=_normalize_icon_url(icon_raw),
    )


def _buy_sell_chaos(
    line: dict[str, Any],
    pairs: list[dict[str, Any]],
    core: dict[str, Any],
    game: str,
) -> tuple[float, float]:
    ce_detail = _chaos_equivalent_from_pairs(pairs, core, game)
    if ce_detail <= 0:
        return 0.0, 0.0
    ce_line = _overview_line_chaos_hint(line, core, game)
    buy = sell = ce_detail
    if ce_line > 0:
        lo, hi = min(ce_line, ce_detail), max(ce_line, ce_detail)
        if hi / lo <= _LINE_DETAIL_MAX_SPREAD:
            buy, sell = lo, hi
    pv_pay = (1.0 / buy) if buy > 0 else 0.0
    return pv_pay, sell


def _fetch_exchange_rates_detailed(
    league: str,
    ninja_type: str,
    category: str,
    game: str,
    overview_url: str,
    details_url: str,
) -> list[CurrencyRate]:
    overview = _request(overview_url, {"league": league, "type": ninja_type})
    if not overview:
        return []

    lines = overview.get("lines") or []
    items_by_id: dict[str, dict[str, Any]] = {i["id"]: i for i in overview.get("items") or [] if i.get("id")}
    core = overview.get("core") or {}
    overview_only = _exchange_overview_only()

    def build_rate_from_overview(line: dict[str, Any]) -> Optional[CurrencyRate]:
        lid = line.get("id")
        if not lid:
            return None
        meta = items_by_id.get(lid)
        if not meta:
            return None
        return _build_rate_from_overview_only(line, meta, core, game, category)

    def build_rate(line: dict[str, Any]) -> Optional[CurrencyRate]:
        lid = line.get("id")
        if not lid:
            return None
        meta = items_by_id.get(lid)
        if not meta:
            return None
        details_id = meta.get("detailsId")
        if not details_id:
            return None
        detail = _request(details_url, {
            "league": league,
            "type": ninja_type,
            "id": details_id,
        })
        _detail_delay()
        if not detail:
            return None
        pairs = detail.get("pairs") or []
        ce = _chaos_equivalent_from_pairs(pairs, core, game)
        if ce <= 0:
            return None
        pay_v, recv_v = _buy_sell_chaos(line, pairs, core, game)
        if pay_v <= 0 or recv_v <= 0:
            return None
        name = meta.get("name") or (detail.get("item") or {}).get("name") or "Unknown"
        icon_raw = (meta.get("icon") if meta else None) or (detail.get("item") or {}).get("icon")
        vol = int(float(line.get("volumePrimaryValue") or 0))
        half = vol // 2
        anchors = frozenset(
            p.get("id")
            for p in pairs
            if p.get("id") in ("chaos", "divine", "exalted")
        )
        return CurrencyRate(
            name=name,
            chaos_equivalent=ce,
            pay_value=pay_v,
            receive_value=recv_v,
            pay_count=half,
            receive_count=vol - half,
            pay_listings=max(1, half) if anchors else 0,
            receive_listings=max(1, vol - half) if anchors else 0,
            anchors=anchors,
            category=category,
            icon=_normalize_icon_url(icon_raw),
        )

    # One category at a time, one /details after another (avoids 429 from parallel bursts).
    results: list[CurrencyRate] = []
    for line in lines:
        r = build_rate_from_overview(line) if overview_only else build_rate(line)
        if r is not None:
            results.append(r)

    results.sort(key=lambda x: x.chaos_equivalent, reverse=True)
    return results


def _stream_deadline() -> float:
    sec = float(getattr(config, "RATES_STREAM_MAX_SEC", 600) or 600)
    return time.time() + max(30.0, sec)


def _check_stream_deadline(deadline: float) -> None:
    if time.time() > deadline:
        raise TimeoutError(
            "Rates fetch exceeded RATES_STREAM_MAX_SEC — try Exchange overview-only in Settings or a quieter time."
        )


def _iter_poe1_economy_batches(
    league: str,
    deadline: Optional[float],
) -> Iterator[tuple[int, int, str, list[CurrencyRate]]]:
    sc_types = getattr(config, "POE1_STASH_CURRENCY_TYPES", [])
    ex_types = getattr(config, "POE1_EXCHANGE_TYPES", [])
    si_types = getattr(config, "POE1_STASH_ITEM_TYPES", [])
    total = max(1, 1 + len(ex_types) + (1 if si_types else 0))
    merged: list[CurrencyRate] = []
    idx = 0
    if deadline is not None:
        _check_stream_deadline(deadline)
    for ninja_type, label in sc_types:
        data = _request(POE1_STASH_CURRENCY_URL, {"league": league, "type": ninja_type})
        if data and data.get("lines") is not None:
            merged.extend(_parse_stash_currency_lines(data, category=label))
    idx += 1
    merged.sort(key=lambda x: x.chaos_equivalent, reverse=True)
    yield (idx, total, "Stash currency", list(merged))

    for ninja_type, label in ex_types:
        if deadline is not None:
            _check_stream_deadline(deadline)
        merged.extend(_fetch_exchange_rates_detailed(
            league, ninja_type, label, "poe1", POE1_EXCHANGE_OVERVIEW_URL, POE1_EXCHANGE_DETAILS_URL,
        ))
        _category_pause()
        idx += 1
        merged.sort(key=lambda x: x.chaos_equivalent, reverse=True)
        yield (idx, total, label, list(merged))

    if si_types:
        if deadline is not None:
            _check_stream_deadline(deadline)
        for ninja_type, label in si_types:
            data = _request(POE1_STASH_ITEM_URL, {"league": league, "type": ninja_type})
            if data and data.get("lines") is not None:
                merged.extend(_parse_stash_item_lines(data, category=label))
        idx += 1
        merged.sort(key=lambda x: x.chaos_equivalent, reverse=True)
        yield (idx, total, "Stash items", list(merged))


def _iter_poe2_economy_batches(
    league: str,
    deadline: Optional[float],
) -> Iterator[tuple[int, int, str, list[CurrencyRate]]]:
    types_list = getattr(config, "POE2_ECONOMY_TYPES", [])
    total = len(types_list)
    if total <= 0:
        return
    merged: list[CurrencyRate] = []
    for i, (ninja_type, label) in enumerate(types_list, start=1):
        if deadline is not None:
            _check_stream_deadline(deadline)
        merged.extend(_fetch_exchange_rates_detailed(
            league, ninja_type, label, "poe2", POE2_EXCHANGE_OVERVIEW_URL, POE2_EXCHANGE_DETAILS_URL,
        ))
        if i < total:
            _category_pause()
        merged.sort(key=lambda x: x.chaos_equivalent, reverse=True)
        yield (i, total, label, list(merged))


def iter_currency_rates_batches(league: str, game: str) -> Iterator[tuple[int, int, str, list[CurrencyRate]]]:
    """
    Yield (1-based index, total_batches, category_label, accumulated_rates) after each batch.
    Used by SSE /api/economy/stream (rates + flips share one pass) so the UI can render category-by-category.
    """
    g = (game or "poe2").lower()
    if g not in ("poe1", "poe2"):
        g = "poe2"
    deadline = _stream_deadline()
    if g == "poe1":
        yield from _iter_poe1_economy_batches(league, deadline)
    else:
        yield from _iter_poe2_economy_batches(league, deadline)


def store_currency_rates_cache(league: str, game: str, rates: list[CurrencyRate]) -> None:
    """Write merged rates into the same TTL key as get_currency_rates (after streaming completes)."""
    g = (game or "poe2").lower()
    if g not in ("poe1", "poe2"):
        g = "poe2"
    ov = 1 if _exchange_overview_only() else 0
    cache_key = f"currency_{g}_{league}_ov{ov}"
    ttl = _cache_ttl()
    if ttl > 0:
        cache_set(cache_key, rates)


def _fetch_poe1_full_economy(league: str) -> list[CurrencyRate]:
    last: list[CurrencyRate] = []
    for _i, _t, _l, merged in _iter_poe1_economy_batches(league, None):
        last = merged
    return last


def _fetch_poe2_full_economy(league: str) -> list[CurrencyRate]:
    last: list[CurrencyRate] = []
    for _i, _t, _l, merged in _iter_poe2_economy_batches(league, None):
        last = merged
    return last


def get_currency_rates(league: str = config.LEAGUE_POE2, game: str = config.GAME) -> list[CurrencyRate]:
    """Fetch full economy from poe.ninja (per-game categories in config.py)."""
    g = (game or "poe2").lower()
    if g not in ("poe1", "poe2"):
        g = "poe2"

    ov = 1 if _exchange_overview_only() else 0
    cache_key = f"currency_{g}_{league}_ov{ov}"

    def compute() -> list[CurrencyRate]:
        if g == "poe1":
            return _fetch_poe1_full_economy(league)
        return _fetch_poe2_full_economy(league)

    return get_or_compute(cache_key, _cache_ttl(), compute)


def get_item_prices(item_type: str, league: str = config.LEAGUE_POE2, game: str = config.GAME) -> list[ItemPrice]:
    """Fetch item prices for a given category from poe.ninja."""
    cache_key = f"item_{game}_{league}_{item_type}"

    def compute() -> list[ItemPrice]:
        data = _request(config.POE_NINJA_ITEM_URL, {
            "league": league,
            "type": item_type,
            "language": "en",
            "game": game,
        })
        if not data or "lines" not in data:
            return []

        items: list[ItemPrice] = []
        for line in data["lines"]:
            items.append(ItemPrice(
                name=line.get("name", "Unknown"),
                chaos_value=line.get("chaosValue", 0.0),
                divine_value=line.get("divineValue", 0.0),
                exalted_value=line.get("exaltedValue", 0.0),
                count=line.get("count", 0),
                listing_count=line.get("listingCount", 0),
                item_type=item_type,
                icon=_normalize_icon_url(line.get("icon")),
            ))

        items.sort(key=lambda i: i.chaos_value, reverse=True)
        return items

    return get_or_compute(cache_key, _cache_ttl(), compute)


def iter_crafting_item_batches(league: str, game: str) -> Iterator[tuple[int, int, str, List[ItemPrice]]]:
    """
    Yield (index, total, category_name, accumulated items) after each CRAFTING_CATEGORIES fetch.
    """
    cats = list(getattr(config, "CRAFTING_CATEGORIES", []) or [])
    total = max(1, len(cats))
    acc: list[ItemPrice] = []
    deadline = _stream_deadline()
    if not cats:
        yield (1, 1, "(none)", [])
        return
    for i, category in enumerate(cats, start=1):
        if deadline is not None:
            _check_stream_deadline(deadline)
        items = get_item_prices(category, league, game)
        acc.extend(items)
        acc.sort(key=lambda x: x.chaos_value * x.count, reverse=True)
        time.sleep(0.2)
        yield (i, total, str(category), list(acc))


def get_all_crafting_items(league: str = config.LEAGUE_POE2, game: str = config.GAME) -> list[ItemPrice]:
    """Fetch items across all crafting categories."""
    last: list[ItemPrice] = []
    for _i, _t, _l, merged in iter_crafting_item_batches(league, game):
        last = merged
    return last


def _tattoo_color_from_image(img: str) -> str:
    """Map poe.ninja tattoo item image to attribute / vendor group."""
    if "CommonStr" in img or "StrTatttoo" in img:
        return "STR"
    if "CommonDex" in img or "DexTatttoo" in img:
        return "DEX"
    if "CommonInt" in img or "IntTatttoo" in img:
        return "INT"
    if "Unique" in img:
        return "Journey"
    return "Other"


def get_poe1_tattoo_color_by_name(league: str) -> dict[str, str]:
    """Tattoo name → STR/DEX/INT/Journey/Other from exchange overview metadata (no /details)."""
    cache_key = f"poe1_tattoo_colors_{league}"

    def compute() -> dict[str, str]:
        out: dict[str, str] = {}
        data = _request(POE1_EXCHANGE_OVERVIEW_URL, {"league": league, "type": "Tattoo", "language": "en"})
        for it in (data or {}).get("items") or []:
            name = it.get("name") or ""
            img = str(it.get("image") or "")
            if name:
                out[name] = _tattoo_color_from_image(img)
        return out

    return get_or_compute(cache_key, _cache_ttl(), compute)


def get_poe1_essence_exchange_rates(league: str) -> list[CurrencyRate]:
    """Essences (Deafening, …) — separate exchange category on poe.ninja (not in default POE1 merge)."""
    cache_key = f"poe1_essence_exchange_{league}"

    def compute() -> list[CurrencyRate]:
        merged = _fetch_exchange_rates_detailed(
            league, "Essence", "Essences", "poe1", POE1_EXCHANGE_OVERVIEW_URL, POE1_EXCHANGE_DETAILS_URL,
        )
        _category_pause()
        return merged

    return get_or_compute(cache_key, _cache_ttl(), compute)


def clear_cache() -> None:
    """Clear all cached data to force fresh fetches."""
    cache_clear()
