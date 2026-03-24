# Releasing POE Trade Flipping

Checklist for maintainers before publishing a **version tag** (triggers [`.github/workflows/release.yml`](.github/workflows/release.yml): Windows + macOS bundles and **`SHA256SUMS-release.txt`**).

## 1. Changelog

1. Open **`CHANGELOG.md`**.
2. Move everything under **`[Unreleased]`** into a new section:

   `## [X.Y.Z] — YYYY-MM-DD`

3. Restore an empty **`[Unreleased]`** (or leave a short placeholder under it).
4. Match **[Semantic Versioning](https://semver.org/)** for **`X.Y.Z`**.

## 2. Quality checks

```bash
python -m unittest discover -s tests -v
```

Fix failures before tagging. Optional: run **`pyinstaller`** locally (see **`CONTRIBUTING.md`**) if you want to sanity-check binaries.

## 3. Optional polish

- **Screenshots:** add PNGs under **`docs/screenshots/`** and embed in **`README.md`** (see **`docs/screenshots/README.md`**).
- **Community:** set **`COMMUNITY_URL`** / **`COMMUNITY_LABEL`** in **`config.py`** if you publish a Discord (or similar) link for **About**.
- **Secrets:** no API keys in **`config.py`** for public builds; users keep **`settings.json`** local.

## 4. Tag and push

Replace **`v0.4.0`** with your version:

```bash
git add -A
git commit -m "Release 0.4.0"
git tag -a v0.4.0 -m "Release 0.4.0"
git push origin main
git push origin v0.4.0
```

## 5. GitHub Release

After CI finishes, open the **Releases** page, edit the new release, and paste the **`CHANGELOG`** section for that version into the description. Users should verify downloads against **`SHA256SUMS-release.txt`**.

## 6. Binaries note

- **Windows:** SmartScreen may warn on unsigned builds.
- **macOS:** unsigned builds may need **Right-click → Open** until notarized (optional, requires Apple tooling).
