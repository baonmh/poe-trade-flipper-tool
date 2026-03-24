"""
POE2 Flipper — Web UI (Flask)
Run: python app.py  → opens browser at http://127.0.0.1:5000 (loopback only)
"""
from __future__ import annotations

import os
import sys
import threading
import webbrowser
import requests
from flask import Flask, jsonify, render_template, request

import config
import settings as cfg
import api.poe_ninja as ninja
from analysis.flip import (
    find_direct_flips,
    key_rates_visible,
    passes_max_buy_budget,
    get_chaos_per_divine,
    get_chaos_per_exalted,
)
from analysis.crafting import get_top_crafting_items, find_bulk_flip_targets
from analysis.convert_tricks import all_trick_results
from analysis.trade_lab import (
    pair_diff_from_sections,
    suggest_from_rates,
)

cfg.load()


def _app_root() -> str:
    """Project dir in dev; PyInstaller extract dir when frozen (templates bundled there)."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__, template_folder=os.path.join(_app_root(), "templates"))


@app.context_processor
def inject_ui_meta() -> dict:
    """About / Support links from config (see DONATION_URL, GITHUB_REPO_URL)."""
    return {
        "donation_url": (getattr(config, "DONATION_URL", "") or "").strip(),
        "donation_label": getattr(config, "DONATION_LABEL", "PayPal") or "PayPal",
        "repo_url": getattr(config, "GITHUB_REPO_URL", "https://github.com/baonmh/poe-trade-flipper-tool"),
    }


def _stat_cards_key_rates(cpd: float, cpe: float) -> list[dict]:
    """Chaos, divine, and exalted benchmarks (same for POE1 and POE2). cpd=c/1div, cpe=c/1ex."""
    ex_per_div = (cpd / cpe) if cpd and cpe else 0.0
    div_per_ex = (cpe / cpd) if cpd and cpe else 0.0
    return [
        {"label": "Chaos per 1 Divine", "value": f"{cpd:,.2f}" if cpd else "—", "sub": "chaos / Divine Orb"},
        {"label": "Chaos per 1 Exalted", "value": f"{cpe:,.2f}" if cpe else "—", "sub": "chaos / Exalted Orb"},
        {
            "label": "Divine ↔ Exalted",
            "value": f"{ex_per_div:.4f} e per 1 d" if ex_per_div else "—",
            "sub": f"{div_per_ex:.4f} d per 1 e" if div_per_ex else "",
        },
    ]


@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ─── API routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/rates")
def api_rates():
    game = cfg.get("GAME")
    league = cfg.active_league()
    rates = ninja.get_currency_rates(league, game)
    key_rates = key_rates_visible(rates, game)
    cpd = get_chaos_per_divine(rates)
    cpe = get_chaos_per_exalted(rates)
    is_poe2 = game == "poe2"
    primary = "exalted" if is_poe2 else "chaos"

    icon_by_name: dict[str, str] = {}
    for r in rates:
        if r.name not in icon_by_name:
            icon_by_name[r.name] = getattr(r, "icon", "") or ""

    rate_rows = []
    for name, val in key_rates.items():
        if val <= 0:
            continue
        rate_rows.append({
            "name": name,
            "icon": icon_by_name.get(name, ""),
            "chaos_value": val,
            "divine_value": round(val / cpd, 4) if cpd else 0.0,
            "exalted_value": round(val / cpe, 4) if cpe else 0.0,
        })

    all_rows = []
    for r in rates:
        if r.chaos_equivalent <= 0:
            continue
        buy_c = round(r.buy_cost_chaos, 2)
        sell_c = round(r.sell_price_chaos, 2)
        if not passes_max_buy_budget(r, game, cpe):
            continue
        row = {
            "name": r.name,
            "icon": getattr(r, "icon", "") or "",
            "category": getattr(r, "category", "") or "",
            "chaos_equivalent": r.chaos_equivalent,
            "buy_cost": buy_c,
            "sell_price": sell_c,
            "spread_pct": round(r.spread_percent, 1),
            "volume": r.volume,
            "listings": r.listings,
        }
        raw_chaos = r.sell_price_chaos - r.buy_cost_chaos
        row["profit_raw_chaos"] = round(raw_chaos, 4)
        if cpe:
            row["buy_cost_ex"] = round(buy_c / cpe, 4)
            row["sell_price_ex"] = round(sell_c / cpe, 4)
            row["profit_raw_ex"] = round(raw_chaos / cpe, 4)
        else:
            row["buy_cost_ex"] = 0.0
            row["sell_price_ex"] = 0.0
            row["profit_raw_ex"] = 0.0
        all_rows.append(row)

    return jsonify({
        "meta": {
            "game": game,
            "league": league,
            "primary": primary,
            "chaos_per_divine": cpd,
            "chaos_per_exalted": cpe,
            "max_buy_chaos": float(cfg.get("MAX_BUY_COST_CHAOS") or 0.0),
            "max_buy_exalted": float(cfg.get("MAX_BUY_COST_EXALTED") or 0.0),
        },
        "stat_cards": _stat_cards_key_rates(cpd, cpe),
        "chaos_per_divine": cpd,
        "chaos_per_exalted": cpe,
        "rates": rate_rows,
        "all_rates": all_rows,
    })


def _flip_row(o, cpe: float, cpd: float, poe2: bool) -> dict:
    # Internal flip math stays in chaos; POE2 surfaces exalted as primary display units.
    row = {
        "name": o.name,
        "buy_currency": o.buy_currency,
        "sell_currency": o.sell_currency,
        "profit_pct": round(o.profit_percent, 1),
        "volume": o.volume,
        "listings": o.listings,
    }
    if poe2 and cpe > 0:
        row["buy_at"] = round(o.buy_at / cpe, 4)
        row["sell_at"] = round(o.sell_at / cpe, 4)
        row["profit"] = round(o.profit_per_trade / cpe, 4)
        row["buy_at_chaos"] = round(o.buy_at, 2)
        row["sell_at_chaos"] = round(o.sell_at, 2)
        row["profit_chaos"] = round(o.profit_per_trade, 2)
    else:
        row["buy_at"] = round(o.buy_at, 2)
        row["sell_at"] = round(o.sell_at, 2)
        row["profit"] = round(o.profit_per_trade, 2)
    if cpe > 0 and not poe2:
        row["buy_at_ex"] = round(o.buy_at / cpe, 4)
        row["sell_at_ex"] = round(o.sell_at / cpe, 4)
        row["profit_ex"] = round(o.profit_per_trade / cpe, 4)
    if cpd > 0:
        div_buy = o.buy_at / cpd
        div_sell = o.sell_at / cpd
        div_p = o.profit_per_trade / cpd
        row["buy_at_div"] = round(div_buy, 4)
        row["sell_at_div"] = round(div_sell, 4)
        row["profit_div"] = round(div_p, 4)
    return row


@app.route("/api/flips")
def api_flips():
    game = cfg.get("GAME")
    league = cfg.active_league()
    rates = ninja.get_currency_rates(league, game)
    cpe = get_chaos_per_exalted(rates)
    cpd = get_chaos_per_divine(rates)
    direct = find_direct_flips(rates, game)
    poe2 = game == "poe2"
    return jsonify({
        "meta": {
            "game": game,
            "league": league,
            "primary": "exalted" if poe2 else "chaos",
            "chaos_per_exalted": cpe,
            "chaos_per_divine": cpd,
        },
        "direct": [_flip_row(o, cpe, cpd, poe2) for o in direct],
    })


@app.route("/api/crafting")
def api_crafting():
    game = cfg.get("GAME")
    league = cfg.active_league()
    items = ninja.get_all_crafting_items(league, game)
    cur = ninja.get_currency_rates(league, game)
    cpe = get_chaos_per_exalted(cur)
    poe2 = game == "poe2"
    hotspots = get_top_crafting_items(items)
    bulk = find_bulk_flip_targets(items)

    def hz(h):
        d = {
            "name": h.name,
            "type": h.item_type,
            "chaos_value": round(h.chaos_value, 2),
            "divine_value": round(h.divine_value, 4),
            "volume": h.trade_volume,
            "listings": h.listing_count,
            "demand_score": round(h.demand_score, 0),
        }
        if cpe:
            d["exalted_value"] = round(h.chaos_value / cpe, 4)
        else:
            d["exalted_value"] = 0.0
        return d

    def bk(i):
        d = {
            "name": i.name,
            "type": i.item_type,
            "chaos_value": round(i.chaos_value, 2),
            "volume": i.count,
            "listings": i.listing_count,
        }
        if cpe:
            d["exalted_value"] = round(i.chaos_value / cpe, 4)
        else:
            d["exalted_value"] = 0.0
        return d

    return jsonify({
        "meta": {
            "game": game,
            "league": league,
            "primary": "exalted" if poe2 else "chaos",
            "chaos_per_exalted": cpe,
        },
        "hotspots": [hz(h) for h in hotspots],
        "bulk": [bk(i) for i in bulk],
    })


@app.route("/api/convert-tricks")
def api_convert_tricks():
    """Vendor / reforge loops: wisdom→portal (POE1), liquid emotions & soul cores (POE2)."""
    game = cfg.get("GAME")
    league = cfg.active_league()
    rates = ninja.get_currency_rates(league, game)
    cpe = get_chaos_per_exalted(rates)
    poe2 = game == "poe2"
    essence: list = []
    tattoo_colors: dict = {}
    if game == "poe1":
        try:
            essence = ninja.get_poe1_essence_exchange_rates(league)
        except Exception:
            essence = []
        try:
            tattoo_colors = ninja.get_poe1_tattoo_color_by_name(league)
        except Exception:
            tattoo_colors = {}
        out = all_trick_results(
            rates, game, cpe,
            poe1_essence_rates=essence,
            poe1_tattoo_colors=tattoo_colors,
        )
    else:
        out = all_trick_results(rates, game, cpe)
    return jsonify({
        "meta": {
            "game": game,
            "league": league,
            "primary": "exalted" if poe2 else "chaos",
            "chaos_per_exalted": cpe,
        },
        "computed": out["computed"],
        "research": out["research"],
    })


@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    return jsonify({"settings": cfg.all_values()})


@app.route("/api/settings", methods=["POST"])
def api_settings_post():
    data = request.json or {}
    key = data.get("key")
    value = data.get("value")
    if not key:
        return jsonify({"error": "missing key"}), 400

    # Find the type from schema (type is stored as name string: "int"/"float"/"str")
    type_map = {"int": int, "float": float, "str": str}
    schema_map = {row["key"]: row["type"] for row in cfg.all_values()}
    if key not in schema_map:
        return jsonify({"error": f"unknown key: {key}"}), 400

    typ = type_map.get(schema_map[key], str)
    try:
        typed_value = typ(value)
    except (ValueError, TypeError):
        return jsonify({"error": f"expected {schema_map[key]}"}), 400

    cfg.set_value(key, typed_value)
    ninja.clear_cache()
    return jsonify({"ok": True, "key": key, "value": typed_value})


@app.route("/api/settings/reset", methods=["POST"])
def api_settings_reset():
    data = request.json or {}
    key = data.get("key")
    if key == "all":
        cfg.reset_all()
    elif key:
        cfg.reset(key)
    ninja.clear_cache()
    return jsonify({"ok": True})


def _rewrite_poe2_league_ids(league_ids: list[str]) -> list[str]:
    """GGG /leagues ignores realm= — ids use POE1 challenge names; map to POE2 trade league names."""
    t1 = getattr(config, "POE1_CHALLENGE_LEAGUE_TOKEN", "") or ""
    t2 = getattr(config, "POE2_CHALLENGE_LEAGUE_TOKEN", "") or ""
    if not t1 or not t2 or t1 == t2:
        return league_ids
    return [lid.replace(t1, t2) if t1 in lid else lid for lid in league_ids]


@app.route("/api/leagues")
def api_leagues():
    # Source: GGG api.pathofexile.com/leagues + POE2 challenge id rewrite (see config.py).
    # GGG: realm= is accepted but /leagues returns the same challenge leagues for pc and poe2.
    raw = (request.args.get("game") or cfg.get("GAME") or "poe2")
    g = str(raw).strip().lower()
    if g in ("poe1", "poe", "1", "pc"):
        realm = "pc"
        poe2_view = False
    else:
        realm = "poe2"
        poe2_view = True
    try:
        resp = requests.get(
            "https://api.pathofexile.com/leagues",
            params={"type": "main", "compact": "1", "realm": realm},
            headers={"User-Agent": "POE2-Flipper/1.0"},
            timeout=8,
        )
        resp.raise_for_status()
        leagues = [l["id"] for l in resp.json()]
        if poe2_view:
            leagues = _rewrite_poe2_league_ids(leagues)
    except Exception:
        leagues = ["Standard", "Hardcore", "Solo Self-Found"]
    return jsonify({"leagues": leagues})


@app.route("/api/clear-cache", methods=["POST"])
def api_clear_cache():
    ninja.clear_cache()
    return jsonify({"ok": True})


@app.route("/api/trade-suggestions")
def api_trade_suggestions():
    """Heuristic good pairs from current rates (direct spreads + light cross hints)."""
    game = cfg.get("GAME")
    league = cfg.active_league()
    rates = ninja.get_currency_rates(league, game)
    cpe = get_chaos_per_exalted(rates)
    out = suggest_from_rates(rates)
    for d in out.get("direct") or []:
        pr = float(d.get("profit_raw_chaos") or 0.0)
        d["profit_raw_ex"] = round(pr / cpe, 4) if cpe else 0.0
    return jsonify({
        "meta": {
            "game": game,
            "league": league,
            "primary": "exalted" if game == "poe2" else "chaos",
            "chaos_per_exalted": cpe,
        },
        **out,
    })


@app.route("/api/trade-pair-diff", methods=["POST"])
def api_trade_pair_diff():
    """
    Auction-style listings: each section has from, to, want, have (I want / I have).
    Pair sections (1–2, 3–4, …) must be opposite directions for the same two currencies.
    """
    data = request.json or {}
    sections = data.get("sections") or []
    if not isinstance(sections, list):
        return jsonify({"error": "sections[] must be a list"}), 400
    out = pair_diff_from_sections(sections)
    return jsonify(out)


# ─── Launch ───────────────────────────────────────────────────────────────────

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False, host="127.0.0.1", port=5000)
