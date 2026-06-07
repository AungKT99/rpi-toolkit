"""
dashboard.py — Live status dashboard screen.
Shows real-time CPU temperature, disk usage, and
the state of each monitored systemd service.
Auto-refreshes every 5 seconds.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Static, Label, DataTable, Log
)
from textual.containers import Horizontal, Vertical, Container
from textual.reactive import reactive
from textual import work
from textual.timer import Timer
from textual.css.query import NoMatches

import json

INSTALL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(INSTALL_DIR, "config.json")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _get_cpu_temp() -> float | None:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return None


def _get_disk_usage() -> tuple[float, float, float] | None:
    try:
        total, used, free = shutil.disk_usage("/")
        return total / 2**30, used / 2**30, (used / total) * 100
    except Exception:
        return None


def _service_status(name: str) -> str:
    try:
        r = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True, text=True
        )
        return r.stdout.strip()
    except Exception:
        return "error"


# ── Widgets ───────────────────────────────────────────────────────────────────

TEMP_CSS = """
.stat-card {
    border: round $accent;
    padding: 1 2;
    margin: 0 1;
    min-width: 28;
    height: 7;
    content-align: center middle;
    background: $surface;
}

.stat-value {
    text-align: center;
    text-style: bold;
    color: $text;
}

.stat-label {
    text-align: center;
    color: $text-muted;
}

.warn { color: $warning; }
.danger { color: $error; }
.ok { color: $success; }
"""


class StatCard(Static):
    """A simple bordered stat display card."""

    DEFAULT_CSS = """
    StatCard {
        border: round $accent;
        padding: 1 2;
        margin: 0 1;
        min-width: 28;
        height: 7;
        content-align: center middle;
        background: $surface;
    }
    """

    def __init__(self, card_id: str, label: str, value: str = "—", **kwargs):
        super().__init__(**kwargs)
        self._card_id = card_id
        self._label = label
        self._value = value

    def compose(self) -> ComposeResult:
        yield Label(self._label, classes="stat-label")
        yield Label(self._value, id=f"val-{self._card_id}", classes="stat-value")

    def update_value(self, value: str, style: str = "") -> None:
        lbl = self.query_one(f"#val-{self._card_id}", Label)
        lbl.update(value)
        lbl.remove_class("ok", "warn", "danger")
        if style:
            lbl.add_class(style)


class DashboardScreen(Screen):
    """Full-screen live dashboard."""

    BINDINGS = [
        ("c", "app.push_screen('config')", "⚙ Config"),
        ("q", "app.quit", "Quit"),
        ("r", "refresh_now", "Refresh"),
    ]

    DEFAULT_CSS = """
    DashboardScreen {
        background: $background;
    }

    #stats-row {
        height: 9;
        margin: 1 1 0 1;
    }

    #services-panel {
        border: round $accent;
        margin: 1;
        padding: 1 2;
        height: auto;
    }

    #services-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #device-banner {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding: 1;
        margin: 0 1;
    }

    StatCard Label {
        width: 100%;
        text-align: center;
    }

    .stat-label {
        color: $text-muted;
        margin-bottom: 1;
    }

    .stat-value {
        text-style: bold;
    }

    .ok    { color: $success; }
    .warn  { color: $warning; }
    .danger { color: $error; }

    DataTable {
        height: auto;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        config = _load_config()
        device = config.get("device_name", "rpi-toolkit")

        yield Header(show_clock=True)

        yield Label(f"🍓  {device}  —  Live Monitor", id="device-banner")

        with Horizontal(id="stats-row"):
            yield StatCard("temp",  "🌡  CPU Temperature", "—", id="card-temp")
            yield StatCard("disk",  "💾  Disk Usage",       "—", id="card-disk")
            yield StatCard("free",  "📦  Free Space",        "—", id="card-free")

        with Vertical(id="services-panel"):
            yield Label("⚙  Monitored Services", id="services-title")
            yield DataTable(id="svc-table", show_header=True, cursor_type="none")

        yield Footer()

    def on_mount(self) -> None:
        # Set up service table columns
        table: DataTable = self.query_one("#svc-table", DataTable)
        table.add_columns("Service", "Status")
        # First paint
        self._do_refresh()
        # Auto-refresh every 5 seconds
        self.set_interval(5, self._do_refresh)

    def action_refresh_now(self) -> None:
        self._do_refresh()

    def _do_refresh(self) -> None:
        config = _load_config()
        self._update_temp(config)
        self._update_disk(config)
        self._update_services(config)

    def _update_temp(self, config: dict) -> None:
        card: StatCard = self.query_one("#card-temp", StatCard)
        temp = _get_cpu_temp()
        threshold = config.get("temp_threshold_celsius", 75.0)
        if temp is None:
            card.update_value("N/A")
        elif temp > threshold:
            card.update_value(f"{temp:.1f} °C", "danger")
        elif temp > threshold * 0.85:
            card.update_value(f"{temp:.1f} °C", "warn")
        else:
            card.update_value(f"{temp:.1f} °C", "ok")

    def _update_disk(self, config: dict) -> None:
        disk_card: StatCard = self.query_one("#card-disk", StatCard)
        free_card: StatCard = self.query_one("#card-free", StatCard)
        usage = _get_disk_usage()
        threshold = config.get("disk_threshold_percent", 85)
        if usage is None:
            disk_card.update_value("N/A")
            free_card.update_value("N/A")
        else:
            total_gb, used_gb, pct = usage
            free_gb = total_gb - used_gb
            style = "danger" if pct > threshold else ("warn" if pct > threshold * 0.9 else "ok")
            disk_card.update_value(f"{pct:.1f}%  ({used_gb:.1f} / {total_gb:.1f} GB)", style)
            free_card.update_value(f"{free_gb:.1f} GB", style)

    def _update_services(self, config: dict) -> None:
        table: DataTable = self.query_one("#svc-table", DataTable)
        table.clear()
        services = config.get("services_to_monitor", [])
        if not services:
            table.add_row("—", "no services configured")
            return
        for svc in services:
            status = _service_status(svc)
            indicator = "✅ active" if status == "active" else f"❌ {status}"
            table.add_row(svc, indicator)
