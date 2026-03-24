"""
Rich terminal display for POE Trade Flipping.
"""
from __future__ import annotations

import datetime

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

GOLD = "yellow"
GREEN = "bright_green"
RED = "bright_red"
CYAN = "cyan"
DIM = "dim"
WHITE = "white"


def _chaos(value: float) -> str:
    return f"[{GOLD}]{value:,.1f}c[/{GOLD}]"


def _divine(value: float) -> str:
    if value >= 0.01:
        return f"[{CYAN}]{value:.2f}d[/{CYAN}]"
    return f"[{DIM}]<0.01d[/{DIM}]"


def _pct(value: float, good_threshold: float = 3.0) -> str:
    color = GREEN if value >= good_threshold else (GOLD if value > 0 else RED)
    return f"[{color}]{value:+.1f}%[/{color}]"


def _volume(v: int) -> str:
    color = GREEN if v >= 20 else (GOLD if v >= 5 else RED)
    return f"[{color}]{v:,}[/{color}]"


def header(league: str, game: str) -> None:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    console.print(Panel(
        f"[bold {GOLD}]POE Trade Flipping[/bold {GOLD}]  "
        f"[{DIM}]League:[/{DIM}] [{WHITE}]{league}[/{WHITE}]  "
        f"[{DIM}]Game:[/{DIM}] [{WHITE}]{game.upper()}[/{WHITE}]  "
        f"[{DIM}]Updated:[/{DIM}] [{WHITE}]{now}[/{WHITE}]",
        box=box.DOUBLE_EDGE,
        style="bold",
    ))


def show_key_rates(rates: dict[str, float], chaos_per_div: float, chaos_per_ex: float) -> None:
    table = Table(
        title="[bold]Key Currency Rates (in Chaos)[/bold]",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style=f"bold {GOLD}",
    )
    table.add_column("Currency", style="white", min_width=24)
    table.add_column("Chaos Value", justify="right", min_width=14)
    table.add_column("In Divines", justify="right", min_width=12)

    for name, chaos_val in rates.items():
        if chaos_val <= 0:
            continue
        div_val = chaos_val / chaos_per_div if chaos_per_div > 0 else 0
        table.add_row(
            name,
            _chaos(chaos_val),
            _divine(div_val),
        )

    console.print(table)
    console.print(
        f"  [{DIM}]Reference:[/{DIM}] "
        f"1 Divine = {_chaos(chaos_per_div)}  |  "
        f"1 Exalted = {_chaos(chaos_per_ex)}\n"
    )


def show_direct_flips(opportunities: list) -> None:
    if not opportunities:
        console.print(f"[{DIM}]No direct flip opportunities found above threshold.[/{DIM}]\n")
        return

    table = Table(
        title="[bold]Direct Flip Opportunities (Buy → Sell)[/bold]",
        box=box.SIMPLE_HEAVY,
        header_style=f"bold {GOLD}",
    )
    table.add_column("#", justify="right", style=DIM, width=3)
    table.add_column("Pair", min_width=28)
    table.add_column("Buy At", justify="right", min_width=10)
    table.add_column("Sell At", justify="right", min_width=10)
    table.add_column("Profit/unit", justify="right", min_width=12)
    table.add_column("Profit %", justify="right", min_width=10)
    table.add_column("Volume", justify="right", min_width=8)

    for i, opp in enumerate(opportunities[:15], 1):
        table.add_row(
            str(i),
            opp.name,
            _chaos(opp.buy_at),
            _chaos(opp.sell_at),
            _chaos(opp.profit_per_trade),
            _pct(opp.profit_percent),
            _volume(opp.volume),
        )

    console.print(table)
    console.print(f"  [{DIM}]Showing top 15. Profit % = (sell-buy)/buy × 100[/{DIM}]\n")


def show_crafting_hotspots(hotspots: list) -> None:
    if not hotspots:
        console.print(f"[{DIM}]No crafting hotspot data available.[/{DIM}]\n")
        return

    table = Table(
        title="[bold]Top Crafting Materials by Demand[/bold]",
        box=box.SIMPLE_HEAVY,
        header_style=f"bold {GOLD}",
    )
    table.add_column("#", justify="right", style=DIM, width=3)
    table.add_column("Item", min_width=28)
    table.add_column("Type", min_width=14, style=DIM)
    table.add_column("Price (c)", justify="right", min_width=10)
    table.add_column("Price (d)", justify="right", min_width=10)
    table.add_column("Volume", justify="right", min_width=8)
    table.add_column("Demand Score", justify="right", min_width=14)

    for i, h in enumerate(hotspots, 1):
        table.add_row(
            str(i),
            h.name,
            h.item_type,
            _chaos(h.chaos_value),
            _divine(h.divine_value),
            _volume(h.trade_volume),
            f"[{CYAN}]{h.demand_score:,.0f}[/{CYAN}]",
        )

    console.print(table)
    console.print(
        f"  [{DIM}]Demand Score = chaos_value × √volume  "
        f"(higher = more player demand)[/{DIM}]\n"
    )


def show_bulk_targets(items: list) -> None:
    if not items:
        console.print(f"[{DIM}]No bulk flip targets found.[/{DIM}]\n")
        return

    table = Table(
        title="[bold]Bulk Buy/Sell Targets (High Volume Items)[/bold]",
        box=box.SIMPLE_HEAVY,
        header_style=f"bold {GOLD}",
    )
    table.add_column("#", justify="right", style=DIM, width=3)
    table.add_column("Item", min_width=28)
    table.add_column("Type", min_width=14, style=DIM)
    table.add_column("Price (c)", justify="right", min_width=10)
    table.add_column("Listings", justify="right", min_width=10)
    table.add_column("Volume", justify="right", min_width=8)

    for i, item in enumerate(items, 1):
        table.add_row(
            str(i),
            item.name,
            item.item_type,
            _chaos(item.chaos_value),
            str(item.listing_count),
            _volume(item.count),
        )

    console.print(table)


def show_config(rows: list[dict]) -> None:
    """Display all settings in a formatted table."""
    table = Table(
        title="[bold]Settings[/bold]",
        box=box.SIMPLE_HEAVY,
        header_style=f"bold {GOLD}",
        show_footer=False,
    )
    table.add_column("#", justify="right", style=DIM, width=3)
    table.add_column("Setting", min_width=22)
    table.add_column("Current Value", min_width=24)
    table.add_column("Default", min_width=16, style=DIM)
    table.add_column("Description", min_width=40, style=DIM)

    for i, row in enumerate(rows, 1):
        current_str = str(row["current"])
        default_str = str(row["default"])
        # Highlight modified values
        if row["modified"]:
            current_display = f"[{CYAN}]{current_str}[/{CYAN}] [dim]✎[/dim]"
        else:
            current_display = f"[{WHITE}]{current_str}[/{WHITE}]"
        table.add_row(
            str(i),
            row["label"],
            current_display,
            default_str,
            row["description"],
        )

    console.print(table)
    console.print(
        f"  [{DIM}]Enter a number to edit a setting, "
        f"[{CYAN}]r <num>[/{CYAN}][{DIM}] to reset to default, "
        f"[{CYAN}]r all[/{CYAN}][{DIM}] to reset everything.[/{DIM}]\n"
    )


def prompt_setting(label: str, current: object, typ: type) -> str:
    """Prompt user for a new value for a setting."""
    return console.input(
        f"  [{GOLD}]{label}[/{GOLD}] [{DIM}](current: {current!s})[/{DIM}] > "
    ).strip()


def show_error(msg: str) -> None:
    console.print(f"[{RED}][!] {msg}[/{RED}]")


def show_info(msg: str) -> None:
    console.print(f"[{CYAN}][i] {msg}[/{CYAN}]")


def show_loading(msg: str) -> None:
    console.print(f"[{DIM}]... {msg}[/{DIM}]")


def separator() -> None:
    console.rule(style=DIM)
