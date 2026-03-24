# External API inventory (maintainers)

All traffic is **read-only** HTTPS. No Path of Exile login.

## Endpoints

| Host | Used for |
|------|----------|
| `poe.ninja` | Economy stash overview (POE1), exchange overview + **details** (POE1/POE2), item overview (crafting), tattoo overview metadata. |
| `api.pathofexile.com` | Public league list (via `app.py` `/api/leagues`). |

## Client flow (`api/poe_ninja.py`)

1. **POE1 full economy** — stash currency + many exchange **types** (each: overview → N `/details` lines) + stash item types.
2. **POE2 full economy** — exchange types from `POE2_ECONOMY_TYPES` (same overview/detail pattern).
3. **Crafting** — `get_item_prices` per category in `CRAFTING_CATEGORIES` (item overview API).
4. **Convert tricks (POE1)** — extra Essence exchange fetch; tattoo colour map from **exchange overview** only (no details).

## Caching (`api/cache.py`)

- **`POE_NINJA_CACHE_TTL_SEC`** — merged results (`get_currency_rates`, `get_item_prices`, tattoo map, essence list). Single-flight: parallel callers share one fetch.
- **`POE_NINJA_HTTP_CACHE_TTL_SEC`** — raw GET JSON dedup (same URL+params within TTL). Set `0` to disable.

`clear_cache()` (settings save / user refresh) clears both layers.

## Future work (backlog)

- **Feature flags** — optional toggles to skip “heavy” fetches (extra Essence exchange, tattoo overview, full crafting sweep) on slow connections.
- **Fewer `/details` calls** — would need overview-first or sampled details and a richer data model (not only caching).

## Rate limiting

- Sequential `/details` with `POE_NINJA_DETAIL_DELAY_SEC`.
- Pause between exchange categories: `POE_NINJA_CATEGORY_PAUSE_SEC`.
- `_http_get_json` retries with backoff on 429 and network errors.

## Internal JSON (`/api/rates`)

Icons come from poe.ninja overview/detail payloads (CDN URLs, normalized in `api/poe_ninja.py`).

- **`rates[]`** — key currencies: `name`, `icon`, `chaos_value`, `divine_value`, `exalted_value`.
- **`all_rates[]`** — filtered economy rows: `name`, `icon`, `category`, buy/sell/spread/volume/listings, etc.
