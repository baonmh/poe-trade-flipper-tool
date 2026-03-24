"""
POE Trade Flipping
---------------------
Usage:
  python main.py                # interactive menu
  python main.py --all          # run all analyses once and exit
  python main.py --rates        # show key currency rates only
  python main.py --flips        # show flip opportunities only
  python main.py --crafting     # show crafting hotspots only
  python main.py --league NAME  # override league (e.g. "Standard")
  python main.py --watch        # auto-refresh every 60s
"""
from __future__ import annotations

import argparse
import time

import settings as cfg
import api.poe_ninja as ninja
from analysis.flip import (
    find_direct_flips,
    key_rates_visible,
    get_chaos_per_divine,
    get_chaos_per_exalted,
)
from analysis.crafting import get_top_crafting_items, find_bulk_flip_targets
from display.rich_display import (
    console,
    header,
    separator,
    show_key_rates,
    show_direct_flips,
    show_crafting_hotspots,
    show_bulk_targets,
    show_config,
    prompt_setting,
    show_error,
    show_info,
    show_loading,
)


# ─── Data fetch helpers ──────────────────────────────────────────────────────

def fetch_currency():
    show_loading("Fetching currency rates from poe.ninja...")
    rates = ninja.get_currency_rates(cfg.active_league(), cfg.get("GAME"))
    if not rates:
        show_error("Failed to fetch currency rates. Check your internet connection.")
    return rates


def fetch_crafting():
    show_loading("Fetching crafting material prices (this may take a moment)...")
    items = ninja.get_all_crafting_items(cfg.active_league(), cfg.get("GAME"))
    if not items:
        show_info("No crafting data returned. The league may not have data yet.")
    return items


# ─── View functions ───────────────────────────────────────────────────────────

def view_rates() -> None:
    rates = fetch_currency()
    if not rates:
        return
    key_rates = key_rates_visible(rates, cfg.get("GAME"))
    cpd = get_chaos_per_divine(rates)
    cpe = get_chaos_per_exalted(rates)
    show_key_rates(key_rates, cpd, cpe)


def view_flips() -> None:
    rates = fetch_currency()
    if not rates:
        return
    show_loading("Calculating direct flip opportunities...")
    direct = find_direct_flips(rates, cfg.get("GAME"))
    show_direct_flips(direct)



def view_crafting() -> None:
    items = fetch_crafting()
    if not items:
        return
    hotspots = get_top_crafting_items(items)
    show_crafting_hotspots(hotspots)

    bulk = find_bulk_flip_targets(items)
    show_bulk_targets(bulk)


def view_all() -> None:
    header(cfg.active_league(), cfg.get("GAME"))
    separator()
    view_rates()
    separator()
    view_flips()
    separator()
    view_crafting()


# ─── Config screen ────────────────────────────────────────────────────────────

def view_config_screen() -> None:
    """Interactive settings editor."""
    while True:
        rows = cfg.all_values()
        header(cfg.active_league(), cfg.get("GAME"))
        show_config(rows)

        choice = console.input("  [bold]> [/bold]").strip().lower()

        if not choice or choice in ("b", "back", "q"):
            break

        # Reset all
        if choice in ("r all", "reset all"):
            cfg.reset_all()
            ninja.clear_cache()
            show_info("All settings reset to defaults.")
            continue

        # Reset single: "r 3"
        if choice.startswith("r "):
            idx_str = choice[2:].strip()
            if idx_str.isdigit():
                idx = int(idx_str) - 1
                if 0 <= idx < len(rows):
                    key = rows[idx]["key"]
                    cfg.reset(key)
                    ninja.clear_cache()
                    show_info(f"Reset '{rows[idx]['label']}' to default: {rows[idx]['default']}")
                else:
                    show_error(f"Invalid number: {idx_str}")
            else:
                show_error(f"Usage: r <number>  or  r all")
            continue

        # Edit by number
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(rows):
                row = rows[idx]
                raw = prompt_setting(row["label"], row["current"], row["type"])
                if not raw:
                    continue
                try:
                    if row["type"] is int:
                        new_val = int(raw)
                    elif row["type"] is float:
                        new_val = float(raw)
                    else:
                        new_val = raw
                    cfg.set_value(row["key"], new_val)
                    ninja.clear_cache()
                    show_info(f"{row['label']} → {new_val}")
                except ValueError:
                    show_error(f"Expected {row['type'].__name__}, got: {raw!r}")
            else:
                show_error(f"Invalid number: {choice}")
        else:
            show_error(f"Unknown input: {choice!r}")

        console.print()


# ─── Interactive menu ─────────────────────────────────────────────────────────

MENU = """
[bold yellow]═══════════════════════════════[/bold yellow]
[bold]  POE Trade Flipping — Main Menu[/bold]
[bold yellow]═══════════════════════════════[/bold yellow]
  [cyan]1[/cyan]  Currency rates (chaos/div/ex)
  [cyan]2[/cyan]  Flip opportunities
  [cyan]3[/cyan]  Crafting material hotspots
  [cyan]4[/cyan]  Run all analyses
  [cyan]s[/cyan]  Settings / Config
  [cyan]6[/cyan]  Clear cache & refresh
  [cyan]q[/cyan]  Quit
"""


def interactive() -> None:
    while True:
        console.print(MENU)
        console.print(
            f"  [dim]League:[/dim] [white]{cfg.active_league()}[/white]  "
            f"[dim]Game:[/dim] [white]{cfg.get('GAME').upper()}[/white]"
        )
        choice = console.input("\n  [bold]> [/bold]").strip().lower()

        if choice == "q":
            console.print("[dim]Goodbye.[/dim]")
            break
        elif choice == "1":
            header(cfg.active_league(), cfg.get("GAME"))
            view_rates()
        elif choice == "2":
            header(cfg.active_league(), cfg.get("GAME"))
            view_flips()
        elif choice == "3":
            header(cfg.active_league(), cfg.get("GAME"))
            view_crafting()
        elif choice == "4":
            view_all()
        elif choice == "s":
            view_config_screen()
        elif choice == "6":
            ninja.clear_cache()
            show_info("Cache cleared. Data will be re-fetched on next query.")
        else:
            show_error(f"Unknown option: {choice!r}")

        console.print()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    cfg.load()   # load persisted settings first

    parser = argparse.ArgumentParser(
        description="POE Trade Flipping — find profitable trade opportunities"
    )
    parser.add_argument(
        "--league",
        default=None,
        help="League for the current game (sets LEAGUE_POE1 or LEAGUE_POE2 to match GAME)",
    )
    parser.add_argument("--all", action="store_true", dest="run_all",
                        help="Run all analyses and exit")
    parser.add_argument("--rates", action="store_true", help="Show currency rates")
    parser.add_argument("--flips", action="store_true", help="Show flip opportunities")
    parser.add_argument("--crafting", action="store_true", help="Show crafting hotspots")
    parser.add_argument("--watch", action="store_true",
                        help="Auto-refresh every N seconds (see Settings)")
    args = parser.parse_args()

    # CLI --league flag overrides saved setting for this session only
    if args.league:
        if cfg.get("GAME") == "poe1":
            cfg.set_value("LEAGUE_POE1", args.league)
        else:
            cfg.set_value("LEAGUE_POE2", args.league)

    if args.watch:
        try:
            while True:
                view_all()
                interval = cfg.get("AUTO_REFRESH_INTERVAL")
                show_info(f"Next refresh in {interval}s — Ctrl+C to stop")
                ninja.clear_cache()
                time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[dim]Watch mode stopped.[/dim]")
        return

    if args.run_all:
        view_all()
        return

    if args.rates:
        header(cfg.active_league(), cfg.get("GAME"))
        view_rates()
        return

    if args.flips:
        header(cfg.active_league(), cfg.get("GAME"))
        view_flips()
        return

    if args.crafting:
        header(cfg.active_league(), cfg.get("GAME"))
        view_crafting()
        return

    interactive()


if __name__ == "__main__":
    main()
