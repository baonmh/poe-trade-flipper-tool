# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Public README, contributing guide, changelog, settings example template, and dependency pins for reproducible installs.
- `api/cache.py`: TTL cache + single-flight for poe.ninja; optional HTTP GET dedup (`POE_NINJA_HTTP_CACHE_TTL_SEC`); `docs/API.md` inventory.

### Changed

- `api/poe_ninja.py`: unified cache/clear through `cache.py`; `config.py` adds `POE_NINJA_CACHE_TTL_SEC` / `POE_NINJA_HTTP_CACHE_TTL_SEC`.

---

## [0.1.0] — 2026-03-24

### Added

- Initial open-source release: Flask web UI, poe.ninja integration for POE1/POE2 (rates, flips, crafting, convert tricks, trade lab), settings persistence.

