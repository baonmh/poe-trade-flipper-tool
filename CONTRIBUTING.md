# Contributing

Thanks for helping improve POE Trade Flipping.

## How to contribute

1. Open an **issue** first for larger changes (refactors, new data sources) so we can align on direction.
2. **Fork** the repository and create a branch from `main`.
3. Keep pull requests **focused** (one feature or fix per PR).
4. Match existing **code style** (formatting, naming, minimal unrelated diffs).
5. If you change behavior visible in the UI, add a short note in **CHANGELOG.md** under `[Unreleased]`.
6. Optional: add or refresh **README screenshots** under **`docs/screenshots/`** (see **`docs/screenshots/README.md`**).

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

### Tests

Smoke tests (no live poe.ninja / GGG calls; economy routes mocked; **`/api/leagues`** tests offline fallback; plus **`POST`** **`/api/trade-pair-diff`** and **`/api/clear-cache`**):

```bash
python -m unittest discover -s tests -v
```

### PyInstaller (optional)

To build the **PyInstaller** folder locally on **Windows or macOS** (see `poe-trade-flipping.spec`):

```bash
pip install -r requirements-build.txt
pyinstaller poe-trade-flipping.spec
```

### Tagged releases (maintainers)

Full step-by-step checklist: **[RELEASING.md](RELEASING.md)** (changelog edit, tests, tag commands, GitHub Release notes, checksums).

The [Release workflow](.github/workflows/release.yml) builds Windows + macOS bundles and attaches **`poe-trade-flipping-windows.zip`**, **`poe-trade-flipping-macos.zip`**, and **`SHA256SUMS-release.txt`** to the GitHub Release for that tag.

## Maintaining a fork

If you publish your own build: optional donation link and label live in **`config.py`** (`DONATION_URL`, `DONATION_LABEL`). GitHub’s **Sponsor** menu is configured in **`.github/FUNDING.yml`** ([docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository)).

Optional **community** link (e.g. Discord): set **`COMMUNITY_URL`** and **`COMMUNITY_LABEL`** in **`config.py`** — the **About** modal shows them when **`COMMUNITY_URL`** is non-empty.

## What we won’t merge

- Dependencies that phone home or require proprietary keys for basic use.
- Scraping that violates site terms of service.

## Code of conduct

Be respectful in issues and PRs. Maintainers may close discussions that are hostile or off-topic.
