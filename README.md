# POE Trade Flipper

Local **Path of Exile (POE1)** and **Path of Exile 2** economy dashboard: browse **currency rates** from [poe.ninja](https://poe.ninja), spot **direct flips**, explore **crafting** hotspots, use **Trade Lab** pair math, and check **convert tricks** (vendor / Harvest / tattoos). Runs in your browser; **no Path of Exile login** and no API keys required.

**Repository:** [github.com/baonmh/poe-trade-flipper-tool](https://github.com/baonmh/poe-trade-flipper-tool)

[![Tests](https://github.com/baonmh/poe-trade-flipper-tool/actions/workflows/test.yml/badge.svg)](https://github.com/baonmh/poe-trade-flipper-tool/actions/workflows/test.yml)
[![Build Windows](https://github.com/baonmh/poe-trade-flipper-tool/actions/workflows/build-windows.yml/badge.svg)](https://github.com/baonmh/poe-trade-flipper-tool/actions/workflows/build-windows.yml)

**Latest release:** [GitHub Releases](https://github.com/baonmh/poe-trade-flipper-tool/releases/latest) (Windows + macOS zips and checksums when you use a version tag).

---

## Features

| Area | What it does |
|------|----------------|
| **Rates** | Full economy table with buy/sell chaos (and exalted for POE2), spreads, categories. |
| **Flips** | Direct currency pair opportunities using the same chaos semantics. |
| **Crafting** | Top crafting items + bulk flip hints from poe.ninja item categories. |
| **Convert tricks** | POE1 vendor loops, Harvest lifeforce math, tattoo 3→1; POE2 liquid emotions & soul cores — with optional manual price overrides (saved in the browser). |
| **Trade Lab** | Auction-style listing pairs and spread suggestions. |
| **Settings** | Game (POE1/POE2), leagues, profit/volume thresholds — persisted in `settings.json` when changed in the UI. |

---

## Requirements

- **Python 3.10+** (3.11+ recommended)
- Network access to **poe.ninja** and (for leagues) **GGG public APIs**

---

## Quick start

```bash
git clone https://github.com/baonmh/poe-trade-flipper-tool.git
cd poe-trade-flipper-tool

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Your browser should open **http://127.0.0.1:5000** (shown as localhost). If it does not, open that URL manually. The dev server listens on **loopback only** — not exposed on your LAN.

---

## Prebuilt binaries (optional)

Maintainers build a **PyInstaller** folder bundle with `poe-trade-flipper.spec`:

```bash
pip install -r requirements-build.txt
pyinstaller poe-trade-flipper.spec
```

- **Windows:** run **`dist/poe-trade-flipper/poe-trade-flipper.exe`**.
- **macOS:** run **`dist/poe-trade-flipper/poe-trade-flipper`** from that folder. Unsigned builds may require **Right-click → Open** the first time (Gatekeeper).

**CI on `main`:** [Build Windows](.github/workflows/build-windows.yml) and [Build macOS](.github/workflows/build-macos.yml) attach artifacts with per-folder **`SHA256SUMS.txt`**.

**GitHub Releases:** pushing a version tag like **`v0.2.0`** runs [Release](.github/workflows/release.yml), which publishes **`poe-trade-flipper-windows.zip`**, **`poe-trade-flipper-macos.zip`**, and **`SHA256SUMS-release.txt`** on the release page. Verify zips against the checksum file after download.

---

## Configuration

- Use the in-app **Settings** page to choose **game**, **league**, and flip filters.
- Optional: copy `settings.example.json` to `settings.json` in the project root to override defaults before first run (same keys as the UI).
- **Heavy fetch toggles** (optional): **Settings** page (checkboxes) or **`config.py`** — **`FETCH_POE1_ESSENCE_EXCHANGE`**, **`FETCH_POE1_TATTOO_OVERVIEW`**, **`FETCH_CRAFTING_FULL_SWEEP`** (default on). Turn off to reduce poe.ninja traffic on slow connections — see [docs/API.md](docs/API.md) (“Feature flags”).

League names must match **poe.ninja** for the selected game (e.g. challenge league name for POE1).

---

## Security & privacy

- The app only calls **public** endpoints (poe.ninja economy APIs, GGG league list, etc.). It does **not** log into Path of Exile, the trade site, or store passwords.
- **Manual prices** and UI settings for convert tricks can be stored in **your browser** (localStorage) and/or `settings.json` on disk — keep that file private if you use it.

---

## Limitations & FAQ

**Not affiliated with Grinding Gear Games or poe.ninja.** Fan tool.

**Why do prices differ from the trade site?**  
Data comes from poe.ninja snapshots (buy/sell listings). In-game trade prices move; spreads and fees also differ from a simple chaos conversion.

**Rate limits / slow refresh**  
poe.ninja may throttle heavy use. The app uses delays between detail requests; if you hit HTTP 429, wait and refresh later.

**Random / “uniform EV” rows (Harvest, tattoos, soul cores)**  
True in-game roll weights are not public. Shown “EV” is a **uniform baseline** over listed prices; use Worst/Best as risk hints, not guaranteed profit.

---

## Support the project

Tips are **optional**. You can use **PayPal** via the **Sponsor** button on [the GitHub repository](https://github.com/baonmh/poe-trade-flipper-tool) or the link in the app (**About** → PayPal). Payments are completed on PayPal’s site. This project stays **free and open source** (MIT).

## Architecture (for contributors)

- **`api/poe_ninja.py`** — poe.ninja fetches, parsing, rate limits.
- **`api/cache.py`** — TTL + single-flight + optional per-HTTP response dedup (see [docs/API.md](docs/API.md)).
- **`analysis/`** — flip math, crafting, convert tricks, trade lab.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and small PRs are welcome.

Run **`python -m unittest discover -s tests -v`** for smoke tests (`/` and `/api/settings`; no network).

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## License

[MIT](LICENSE)
