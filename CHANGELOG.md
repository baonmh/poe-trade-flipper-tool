# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] — 2026-03-23

### Added

- **`EXCHANGE_USE_OVERVIEW_ONLY`** (Settings + **`config.py`**, default `False`): exchange economy **without** per-line `/details` — fewer HTTP calls; overview mid-price only so **spread % ≈ 0**; **`/api/rates` `meta.exchange_overview_only`**; Rates subtitle + cache key `…_ov0|1`.
- **`docs/screenshots/README.md`** — maintainer guide for optional README PNGs; root **`README.md`** Screenshots section; **`CONTRIBUTING.md`** pointer.
- **`/api/flips`** **`direct[]`** **`icon`** field (poe.ninja URL for **`sell_currency`**) — **Flips** table uses the same inline icon + letter fallback as **Rates**.
- **Crafting** — **`/api/crafting`** **`hotspots[]`** / **`bulk[]`** expose **`icon`**; **Crafting** page uses **`rateIconInline`**; **`get_item_prices`** normalizes item **`icon`** URLs with **`_normalize_icon_url`**.
- **Support / onboarding:** **`config.py`** **`COMMUNITY_URL`** / **`COMMUNITY_LABEL`** (optional) — link in **About** when set; **`README.md`** **Getting help**; first-run dismissible banner pointing to **About** (**`localStorage`** key **`flipping_about_hint_dismissed_v1`**).
- **Tests:** mocked smoke checks for **`/api/rates`**, **`/api/flips`**, **`/api/crafting`**, **`/api/convert-tricks`**, **`/api/trade-suggestions`**; **`POST /api/trade-pair-diff`** and **`POST /api/clear-cache`**; **`/api/leagues`** fallback when GGG is unreachable (**13** tests; no live poe.ninja / GGG).
- **`RELEASING.md`** — maintainer checklist (changelog, tests, tag, GitHub Release, checksums); linked from **`README.md`** and **`CONTRIBUTING.md`**.
- **Progressive economy load:** **`GET /api/economy/stream`** (SSE) — one JSON envelope per economy category with **`rates`** + **`flips`**; **`meta.stream_progress`** / **`stream_done`**; **`RATES_USE_STREAMING`** / **`FLIPS_USE_STREAMING`** + **`RATES_STREAM_MAX_SEC`** in **`config.py`**; client **`EventSource`** + timeout fallback to **`GET /api/rates`** and **`GET /api/flips`**; cache filled when stream completes.

### Changed

- **Repository and branding:** GitHub **`https://github.com/baonmh/poe-trade-flipping-tool`**; PyInstaller **`poe-trade-flipping.spec`**, output folder **`poe-trade-flipping`**, release zips **`poe-trade-flipping-*.zip`**; in-app strings **POE Trade Flipping**; **`localStorage`** keys **`flipping_*`** with one-time read from legacy **`flipper_*`** where applicable.
- **UX:** clearer **network error** text when the browser cannot reach the Flask app; **Trade Lab** “Refresh suggestions” shows a **spinner row**, no longer reports **Updated** on failure, **Retry** calls the full refresh; header **status** uses **`role="status"`** / **`aria-live="polite"`**.
- **a11y:** **`:focus-visible`** outline rings for links, buttons, nav, game switch, and form controls.
- **Settings:** default **Max Buy** (**POE1** chaos / **POE2** exalted) **999999** so the full economy shows until users lower the cap; **0** still means unlimited.
- **Header:** **About** and support link (**default label** **Buy me a coffee**) on the left with league-style pill styling; **`DONATION_LABEL`** default updated in **`config.py`**.

## [0.3.0] — 2026-03-26

### Added

- **Settings UI** checkboxes for fetch flags (same keys as **`config.py`**); POE1-only flags hidden when game is POE2; **`settings.example.json`** includes the three booleans.
- **`config.py` feature flags** (default `True`): **`FETCH_POE1_ESSENCE_EXCHANGE`**, **`FETCH_POE1_TATTOO_OVERVIEW`**, **`FETCH_CRAFTING_FULL_SWEEP`** — skip extra poe.ninja work for Convert Tricks / Crafting on slow connections; API **`meta`** exposes effective flags; subtitles hint when disabled.

### Changed

- Effective fetch flags read from **`settings`** overrides (`cfg.get`) so UI and `settings.json` apply; **`bool`** supported in **`POST /api/settings`**.

## [0.2.0] — 2026-03-25

### Added

- **`tests/test_smoke.py`** — unittest smoke tests for `/` and `/api/settings`; GitHub Actions **Tests** workflow (`test.yml`) on push/PR to `main`.
- **GitHub Releases** workflow (`release.yml`): push tag `v*` → `poe-trade-flipping-windows.zip`, `poe-trade-flipping-macos.zip`, and `SHA256SUMS-release.txt`.
- **macOS CI** (`build-macos.yml`): PyInstaller artifact on `main` (same spec as Windows).
- **Windows PyInstaller** bundle: `poe-trade-flipping.spec`, `requirements-build.txt`, **Build Windows** artifact + `SHA256SUMS.txt`; frozen app resolves `templates/` via `sys._MEIPASS`.
- GitHub **issue templates** (bug report + feature request).
- Currency **icons** on the Rates page (poe.ninja CDN URLs on `CurrencyRate` and `/api/rates` `icon` fields).
- Public README, contributing guide, changelog, `settings.example.json`, and pinned **`requirements.txt`**.
- **`api/cache.py`**: TTL cache + single-flight for poe.ninja; optional HTTP GET dedup (`POE_NINJA_HTTP_CACHE_TTL_SEC`); **`docs/API.md`** inventory.
- **About** modal + optional donation header link from **`config.py`** (`DONATION_URL`, `DONATION_LABEL`, `GITHUB_REPO_URL`); README “Support the project” (PayPal / PayPal.me).

### Changed

- **UI:** site **footer** (poe.ninja, GGG disclaimer, GitHub, optional Support); **About** copy (first-run hints, stronger price disclaimer); clearer **empty states**; About modal **focus** / **Escape**; flex **layout** with footer.
- **`app.py`**: Flask binds **`127.0.0.1:5000`** (loopback only).
- **API fetch UX:** `fetchJsonOk` for HTTP errors; **Retry** on failed loads (Rates, Flips, Crafting, Convert Tricks, Trade Lab suggestions).
- **`api/poe_ninja.py`**: unified cache through `cache.py`; **`config.py`** adds `POE_NINJA_CACHE_TTL_SEC` / `POE_NINJA_HTTP_CACHE_TTL_SEC`.
- README support section for end users; fork notes in **CONTRIBUTING.md**; **`.github/FUNDING.yml`** YAML-only.

---

## [0.1.0] — 2026-03-24

### Added

- Initial open-source release: Flask web UI, poe.ninja integration for POE1/POE2 (rates, flips, crafting, convert tricks, trade lab), settings persistence.

---

[Unreleased]: https://github.com/baonmh/poe-trade-flipping-tool/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/baonmh/poe-trade-flipping-tool/releases/tag/v0.4.0
[0.3.0]: https://github.com/baonmh/poe-trade-flipping-tool/releases/tag/v0.3.0
[0.2.0]: https://github.com/baonmh/poe-trade-flipping-tool/releases/tag/v0.2.0
[0.1.0]: https://github.com/baonmh/poe-trade-flipping-tool/releases/tag/v0.1.0
