# Contributing

Thanks for helping improve POE Trade Flipper.

## How to contribute

1. Open an **issue** first for larger changes (refactors, new data sources) so we can align on direction.
2. **Fork** the repository and create a branch from `main`.
3. Keep pull requests **focused** (one feature or fix per PR).
4. Match existing **code style** (formatting, naming, minimal unrelated diffs).
5. If you change behavior visible in the UI, add a short note in **CHANGELOG.md** under `[Unreleased]`.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

To build the **PyInstaller** folder locally on **Windows or macOS** (see `poe-trade-flipper.spec`):

```bash
pip install -r requirements-build.txt
pyinstaller poe-trade-flipper.spec
```

### Tagged releases (maintainers)

Update **`CHANGELOG.md`** (move `[Unreleased]` into a dated section), then create and push a version tag, for example:

```bash
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0
```

The [Release workflow](.github/workflows/release.yml) builds Windows + macOS bundles and attaches **`poe-trade-flipper-windows.zip`**, **`poe-trade-flipper-macos.zip`**, and **`SHA256SUMS-release.txt`** to the GitHub Release for that tag.

## Maintaining a fork

If you publish your own build: optional donation link and label live in **`config.py`** (`DONATION_URL`, `DONATION_LABEL`). GitHub’s **Sponsor** menu is configured in **`.github/FUNDING.yml`** ([docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository)).

## What we won’t merge

- Dependencies that phone home or require proprietary keys for basic use.
- Scraping that violates site terms of service.

## Code of conduct

Be respectful in issues and PRs. Maintainers may close discussions that are hostile or off-topic.
