# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **GitHub Releases** workflow (`.github/workflows/release.yml`): push tag `v*` → `poe-trade-flipper-windows.zip`, `poe-trade-flipper-macos.zip`, and `SHA256SUMS-release.txt` on the release.
- **macOS CI** (`.github/workflows/build-macos.yml`): PyInstaller artifact on `main` (same spec as Windows).
- **Windows PyInstaller** bundle: `poe-trade-flipper.spec`, `requirements-build.txt`, GitHub Actions **Build Windows** artifact + `SHA256SUMS.txt`; frozen app resolves `templates/` via `sys._MEIPASS`.
- GitHub **issue templates** (bug report + feature request).
- Currency **icons** on the Rates page (poe.ninja CDN URLs on `CurrencyRate` and `/api/rates` `icon` fields).
- Public README, contributing guide, changelog, settings example template, and dependency pins for reproducible installs.
- `api/cache.py`: TTL cache + single-flight for poe.ninja; optional HTTP GET dedup (`POE_NINJA_HTTP_CACHE_TTL_SEC`); `docs/API.md` inventory.
- **About** modal + optional donation header link from `config.py` (`DONATION_URL`, `DONATION_LABEL`, `GITHUB_REPO_URL`); README “Support the project” section (PayPal / PayPal.me only).

### Changed

- **`app.py`**: Flask binds **`127.0.0.1:5000`** (loopback only); browser opens the same URL.
- **API fetch UX**: `fetchJsonOk` checks HTTP status and surfaces rate-limit / server errors clearly; failed loads show **Retry** on Rates, Flips, Crafting, Convert Tricks, and Trade Lab suggestions.
- `api/poe_ninja.py`: unified cache/clear through `cache.py`; `config.py` adds `POE_NINJA_CACHE_TTL_SEC` / `POE_NINJA_HTTP_CACHE_TTL_SEC`.
- README support section simplified for end users; fork/maintainer notes moved to CONTRIBUTING.md; `.github/FUNDING.yml` trimmed to YAML only.

---

## [0.1.0] — 2026-03-24

### Added

- Initial open-source release: Flask web UI, poe.ninja integration for POE1/POE2 (rates, flips, crafting, convert tricks, trade lab), settings persistence.

