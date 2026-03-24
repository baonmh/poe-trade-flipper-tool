"""
POE2 Flipper Configuration
"""

# === League Settings (one per game — different GGG realms) ===
LEAGUE_POE1 = "Standard"
LEAGUE_POE2 = "Standard"
GAME = "poe2"                # "poe2" or "poe1"

# ── League list source (/api/leagues) ─────────────────────────────────────────
# 1) Fetched from GGG: GET https://api.pathofexile.com/leagues?type=main&compact=1&realm=pc|poe2
#    The public /leagues list does NOT reliably separate POE1 vs POE2 challenge names (realm is
#    effectively ignored); challenge rows follow POE1 naming (e.g. Mirage).
# 2) For POE2 dropdown + poe.ninja, challenge rows are rewritten:
#      POE1_CHALLENGE_LEAGUE_TOKEN → POE2_CHALLENGE_LEAGUE_TOKEN (substring replace on each id).
# 3) Ground truth for trade data: poe.ninja POE2 APIs use ?league=<exact name> — verify with e.g.
#    GET .../poe2/api/economy/exchange/current/overview?league=Fate+of+the+Vaal&type=Currency
# 4) Awakened PoE Trade / Sidekick / official trade site: leagues usually come from GGG *trade*
#    APIs (browser + Cloudflare), not the same public /leagues feed — names should still match
#    in-game / poe.ninja for POE2.
POE1_CHALLENGE_LEAGUE_TOKEN = "Mirage"
POE2_CHALLENGE_LEAGUE_TOKEN = "Fate of the Vaal"

# === poe.ninja API (avoid 429: sequential /details + delays; tune if needed) ===
POE_NINJA_DETAIL_DELAY_SEC = 0.12   # pause after each exchange /details request
POE_NINJA_CATEGORY_PAUSE_SEC = 0.9  # pause after each exchange category completes
# api/cache.py — merged lists (rates, items, tattoo map, essence list)
POE_NINJA_CACHE_TTL_SEC = 240
# Per-GET JSON dedup (0 = off). Reuses identical overview/detail URLs during overlapping refreshes.
POE_NINJA_HTTP_CACHE_TTL_SEC = 120
POE_NINJA_BASE = "https://poe.ninja/api/data"
POE_NINJA_CURRENCY_URL = f"{POE_NINJA_BASE}/currencyoverview"
POE_NINJA_ITEM_URL = f"{POE_NINJA_BASE}/itemoverview"

# === POE1 Harvest (Horticrafting) — lifeforce per full stack (verify in-game; patch-dependent) ===
# Deafening essence reroll: common bench uses 270 Primal Crystallised Lifeforce per 9 essences in the stack.
POE1_HARVEST_ESSENCE_LIFEFORCE_PRIMAL_PER_STACK = 270
POE1_HARVEST_ESSENCE_STACK_SIZE = 9
# Catalyst reroll: 300 Vivid Crystallised Lifeforce per 10 catalysts in the stack.
POE1_HARVEST_CATALYST_LIFEFORCE_VIVID_PER_STACK = 300
POE1_HARVEST_CATALYST_STACK_SIZE = 10

# === Flip Settings ===
MIN_PROFIT_PERCENT = 3.0    # Minimum % profit to flag a flip opportunity
MIN_VOLUME = 5              # Minimum trade volume to consider a pair liquid enough
MIN_BUY_COST_CHAOS = 0.5    # POE1: ignore currencies cheaper than this (chaos)
MIN_BUY_COST_EXALTED = 0.02 # POE2: ignore currencies cheaper than this (exalted)
# Max buy (0 = no limit): hide key rates / spread rows / flips where buying 1 unit costs more than this.
MAX_BUY_COST_CHAOS = 0.0    # POE1: max buy cost (chaos); excludes Mirror-tier when set
MAX_BUY_COST_EXALTED = 0.0  # POE2: max buy cost (exalted)

# === Full economy (poe.ninja exchange `type=` + display label) ===
# POE2: /poe2/api/economy/exchange/current/overview|details — detail fetch per line for accurate chaos.
# Not exposed by poe.ninja today (0 lines): Lineage Gems, Omens, Catalysts — add when API lists them.
POE2_ECONOMY_TYPES: list[tuple[str, str]] = [
    ("Currency", "Currency"),
    ("Fragments", "Fragments"),
    ("Abyss", "Abyssal Bones"),
    ("UncutGems", "Uncut Gems"),
    ("Essences", "Essences"),
    ("SoulCores", "Soul Cores"),
    ("Idols", "Idols"),
    ("Runes", "Runes"),
    ("Expedition", "Expedition"),
    ("Delirium", "Liquid Emotions"),
]

# POE1: stash currency overview (Currency + Fragment) + exchange overview + stash item overview (Wombgift, Incubator).
POE1_STASH_CURRENCY_TYPES: list[tuple[str, str]] = [
    ("Currency", "Currency"),
    ("Fragment", "Fragments"),
]
POE1_EXCHANGE_TYPES: list[tuple[str, str]] = [
    ("Runegraft", "Runegrafts"),
    ("AllflameEmber", "Allflame Embers"),
    ("Tattoo", "Tattoos"),
    ("Omen", "Omens"),
    ("DjinnCoin", "Djinn Coins"),
    ("Artifact", "Artifacts"),
    ("Oil", "Oils"),
]
# One request per type (chaosValue) — avoids hundreds of exchange /details calls (429 risk).
POE1_STASH_ITEM_TYPES: list[tuple[str, str]] = [
    ("Wombgift", "Wombgifts"),
    ("Incubator", "Incubators"),
    ("DivinationCard", "Divination Cards"),
]

# === Crafting Material Categories (poe.ninja item types) ===
CRAFTING_CATEGORIES = [
    "Essence",
    "DivinationCard",
    "Scarab",
    "Oil",
    "Catalyst",
    "Artifact",
    "DeliriumOrb",
]

# === Key Currencies to track ===
KEY_CURRENCIES = [
    "Chaos Orb",
    "Divine Orb",
    "Exalted Orb",
    "Orb of Annulment",
    "Mirror of Kalandra",
    "Orb of Alteration",
    "Regal Orb",
    "Vaal Orb",
    "Orb of Alchemy",
    "Orb of Scouring",
    "Orb of Regret",
    "Gemcutter's Prism",
    "Jeweller's Orb",
]

# === Refresh interval (seconds) ===
AUTO_REFRESH_INTERVAL = 60
