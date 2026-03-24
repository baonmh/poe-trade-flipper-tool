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

## Feature flags (`config.py` + Settings)

Optional **booleans** (default **`True`**) to skip extra poe.ninja work on slow or metered connections. Set in **`config.py`** or the in-app **Settings** page (persisted in `settings.json`); changing in the UI applies on the next API call (cache cleared on save).

| Flag | When `False` |
|------|----------------|
| **`FETCH_POE1_ESSENCE_EXCHANGE`** | Skips the separate POE1 Essence exchange sweep used by Convert Tricks (many `/details`). |
| **`FETCH_POE1_TATTOO_OVERVIEW`** | Skips Tattoo exchange overview metadata (colour map) for Convert Tricks. |
| **`FETCH_CRAFTING_FULL_SWEEP`** | Skips fetching all `CRAFTING_CATEGORIES` item overviews — Crafting page hotspots/bulk stay empty. |

`/api/crafting` **`meta.crafting_full_sweep`** and `/api/convert-tricks` **`meta.fetch_poe1_*`** (POE1 only) report effective flags.

## Future work (backlog)

- **Fewer `/details` calls** on the main economy — would need overview-first or sampled details and a richer data model (not only caching).

## Rate limiting

- Sequential `/details` with `POE_NINJA_DETAIL_DELAY_SEC`.
- Pause between exchange categories: `POE_NINJA_CATEGORY_PAUSE_SEC`.
- `_http_get_json` retries with backoff on 429 and network errors.

## Internal JSON (`/api/rates`)

Icons come from poe.ninja overview/detail payloads (CDN URLs, normalized in `api/poe_ninja.py`).

- **`rates[]`** — key currencies: `name`, `icon`, `chaos_value`, `divine_value`, `exalted_value`.
- **`all_rates[]`** — filtered economy rows: `name`, `icon`, `category`, buy/sell/spread/volume/listings, etc.
