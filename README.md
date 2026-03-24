# POE Trade Flipper

Local **Path of Exile (POE1)** and **Path of Exile 2** economy dashboard: browse **currency rates** from [poe.ninja](https://poe.ninja), spot **direct flips**, explore **crafting** hotspots, use **Trade Lab** pair math, and check **convert tricks** (vendor / Harvest / tattoos). Runs in your browser; **no Path of Exile login** and no API keys required.

**Repository:** [github.com/baonmh/poe-trade-flipper-tool](https://github.com/baonmh/poe-trade-flipper-tool)

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

Your browser should open **http://localhost:5000**. If it does not, open that URL manually.

---

## Configuration

- Use the in-app **Settings** page to choose **game**, **league**, and flip filters.
- Optional: copy `settings.example.json` to `settings.json` in the project root to override defaults before first run (same keys as the UI).

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

## Architecture (for contributors)

- **`api/poe_ninja.py`** — poe.ninja fetches, parsing, rate limits.
- **`api/cache.py`** — TTL + single-flight + optional per-HTTP response dedup (see [docs/API.md](docs/API.md)).
- **`analysis/`** — flip math, crafting, convert tricks, trade lab.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and small PRs are welcome.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## License

[MIT](LICENSE)
