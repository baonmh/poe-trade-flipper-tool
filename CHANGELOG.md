# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Settings UI** checkboxes for fetch flags (same keys as **`config.py`**); POE1-only flags hidden when game is POE2; **`settings.example.json`** includes the three booleans.
- **`config.py` feature flags** (default `True`): **`FETCH_POE1_ESSENCE_EXCHANGE`**, **`FETCH_POE1_TATTOO_OVERVIEW`**, **`FETCH_CRAFTING_FULL_SWEEP`** — skip extra poe.ninja work for Convert Tricks / Crafting on slow connections; API **`meta`** exposes effective flags; subtitles hint when disabled.

### Changed

- Effective fetch flags read from **`settings`** overrides (`cfg.get`) so UI and `settings.json` apply; **`bool`** supported in **`POST /api/settings`**.

## [0.2.0] — 2026-03-25

### Added

- **`tests/test_smoke.py`** — unittest smoke tests for `/` and `/api/settings`; GitHub Actions **Tests** workflow (`test.yml`) on push/PR to `main`.
- **GitHub Releases** workflow (`release.yml`): push tag `v*` → `poe-trade-flipper-windows.zip`, `poe-trade-flipper-macos.zip`, and `SHA256SUMS-release.txt`.
- **macOS CI** (`build-macos.yml`): PyInstaller artifact on `main` (same spec as Windows).
- **Windows PyInstaller** bundle: `poe-trade-flipper.spec`, `requirements-build.txt`, **Build Windows** artifact + `SHA256SUMS.txt`; frozen app resolves `templates/` via `sys._MEIPASS`.
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

[Unreleased]: https://github.com/baonmh/poe-trade-flipper-tool/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/baonmh/poe-trade-flipper-tool/releases/tag/v0.2.0
[0.1.0]: https://github.com/baonmh/poe-trade-flipper-tool/releases/tag/v0.1.0
