"""
config.py — Interactive configuration editor screen.
Lets the user edit all settings in-TUI, then save
config.json and optionally run the full installer.
"""

from __future__ import annotations

import json
import os
import threading

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Input, Switch, Button,
    Label, Static, Log, TabbedContent, TabPane,
    ListView, ListItem,
)
from textual.containers import Horizontal, Vertical, Container, ScrollableContainer
from textual.validation import Number

INSTALL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(INSTALL_DIR, "config.json")

_DEFAULT_CONFIG = {
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "device_name": "Home RPI 5",
    "temp_threshold_celsius": 75.0,
    "disk_threshold_percent": 85,
    "services_to_monitor": ["ssh", "cron", "docker"],
    "ip_notifier": {"enabled": True},
    "schedules": {
        "temp_monitor":     {"enabled": True, "interval_minutes": 10},
        "storage_watcher":  {"enabled": True, "interval_minutes": 60},
        "service_watchdog": {"enabled": True, "interval_minutes": 5},
    },
}


def _load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return dict(_DEFAULT_CONFIG)


def _save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


class SectionTitle(Static):
    DEFAULT_CSS = """
    SectionTitle {
        color: $accent;
        text-style: bold;
        padding: 1 0 0 0;
        margin-bottom: 1;
    }
    """


class FieldRow(Horizontal):
    DEFAULT_CSS = """
    FieldRow {
        height: 3;
        align: left middle;
        margin-bottom: 1;
    }
    FieldRow Label {
        width: 30;
        padding-right: 2;
        color: $text-muted;
    }
    FieldRow Input {
        width: 40;
    }
    FieldRow Switch {
        margin-top: 0;
    }
    """


class ConfigScreen(Screen):
    """Configuration editor screen."""

    BINDINGS = [
        ("escape", "app.pop_screen", "◀ Back"),
        ("ctrl+s",  "save_config",   "Save"),
    ]

    DEFAULT_CSS = """
    ConfigScreen {
        background: $background;
    }

    #config-scroll {
        padding: 0 2;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 1 2;
    }

    #log-panel {
        border: round $accent;
        height: 12;
        margin: 1;
    }

    #btn-row {
        height: 5;
        align: center middle;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }

    .services-list {
        border: round $panel;
        height: 8;
        padding: 0 1;
        margin-top: 1;
    }

    #new-svc-row {
        height: 3;
        align: left middle;
        margin-top: 1;
    }

    #new-svc-row Input {
        width: 30;
        margin-right: 1;
    }
    """

    def compose(self) -> ComposeResult:
        self._config = _load_config()

        yield Header(show_clock=True)

        with TabbedContent():

            # ── Tab 1: General ────────────────────────────────────────────
            with TabPane("🔧 General", id="tab-general"):
                with ScrollableContainer(id="config-scroll"):
                    yield SectionTitle("Telegram")
                    with FieldRow():
                        yield Label("Bot Token")
                        yield Input(
                            value=self._config.get("telegram_bot_token", ""),
                            placeholder="123456:ABC-DEF...",
                            password=True,
                            id="inp-token",
                        )
                    with FieldRow():
                        yield Label("Chat ID")
                        yield Input(
                            value=str(self._config.get("telegram_chat_id", "")),
                            placeholder="123456789",
                            id="inp-chat-id",
                        )

                    yield SectionTitle("Device")
                    with FieldRow():
                        yield Label("Device Name")
                        yield Input(
                            value=self._config.get("device_name", ""),
                            placeholder="Home RPI 5",
                            id="inp-device",
                        )

                    yield SectionTitle("Thresholds")
                    with FieldRow():
                        yield Label("Temp Threshold (°C)")
                        yield Input(
                            value=str(self._config.get("temp_threshold_celsius", 75.0)),
                            placeholder="75.0",
                            id="inp-temp-thresh",
                            validators=[Number(minimum=30, maximum=100)],
                        )
                    with FieldRow():
                        yield Label("Disk Threshold (%)")
                        yield Input(
                            value=str(self._config.get("disk_threshold_percent", 85)),
                            placeholder="85",
                            id="inp-disk-thresh",
                            validators=[Number(minimum=10, maximum=99)],
                        )

            # ── Tab 2: Modules ────────────────────────────────────────────
            with TabPane("📦 Modules", id="tab-modules"):
                with ScrollableContainer():

                    yield SectionTitle("IP Notifier  (systemd — runs on boot)")
                    ip_enabled = self._config.get("ip_notifier", {}).get("enabled", True)
                    with FieldRow():
                        yield Label("Enabled")
                        yield Switch(value=ip_enabled, id="sw-ip")

                    yield SectionTitle("Temperature Monitor")
                    tm = self._config.get("schedules", {}).get("temp_monitor", {})
                    with FieldRow():
                        yield Label("Enabled")
                        yield Switch(value=tm.get("enabled", True), id="sw-temp")
                    with FieldRow():
                        yield Label("Interval (minutes)")
                        yield Input(
                            value=str(tm.get("interval_minutes", 10)),
                            id="inp-temp-int",
                            validators=[Number(minimum=1, maximum=1440)],
                        )

                    yield SectionTitle("Storage Watcher")
                    sw = self._config.get("schedules", {}).get("storage_watcher", {})
                    with FieldRow():
                        yield Label("Enabled")
                        yield Switch(value=sw.get("enabled", True), id="sw-disk")
                    with FieldRow():
                        yield Label("Interval (minutes)")
                        yield Input(
                            value=str(sw.get("interval_minutes", 60)),
                            id="inp-disk-int",
                            validators=[Number(minimum=1, maximum=1440)],
                        )

                    yield SectionTitle("Service Watchdog")
                    wd = self._config.get("schedules", {}).get("service_watchdog", {})
                    with FieldRow():
                        yield Label("Enabled")
                        yield Switch(value=wd.get("enabled", True), id="sw-wd")
                    with FieldRow():
                        yield Label("Interval (minutes)")
                        yield Input(
                            value=str(wd.get("interval_minutes", 5)),
                            id="inp-wd-int",
                            validators=[Number(minimum=1, maximum=1440)],
                        )

            # ── Tab 3: Services ───────────────────────────────────────────
            with TabPane("🛡 Services", id="tab-services"):
                yield Label(
                    "Services to watch (service_watchdog will monitor these):",
                    classes=""
                )
                yield ListView(
                    *[ListItem(Label(s), id=f"svc-{s}")
                      for s in self._config.get("services_to_monitor", [])],
                    id="svc-list",
                )
                with Horizontal(id="new-svc-row"):
                    yield Input(placeholder="e.g. nginx", id="inp-new-svc")
                    yield Button("➕ Add", id="btn-add-svc", variant="primary")
                    yield Button("🗑 Remove Selected", id="btn-rm-svc", variant="warning")

            # ── Tab 4: Apply ──────────────────────────────────────────────
            with TabPane("🚀 Apply", id="tab-apply"):
                yield Label(
                    "Save your config and run the installer to apply all changes.\n"
                    "This will: set up cron jobs, enable/disable systemd service,\n"
                    "install dependencies, and configure logrotate.\n\n"
                    "⚠  Requires root (sudo ./rpi-toolkit)",
                )
                yield Log(id="install-log", highlight=True)

        with Horizontal(id="btn-row"):
            yield Button("💾 Save", id="save-btn", variant="success")
            yield Button("🚀 Save & Apply", id="apply-btn", variant="primary")
            yield Button("✕ Cancel", id="cancel-btn")

        yield Footer()

    # ── Button handlers ───────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.action_save_config()
        elif event.button.id == "apply-btn":
            self.action_save_config()
            self._run_installer()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
        elif event.button.id == "btn-add-svc":
            self._add_service()
        elif event.button.id == "btn-rm-svc":
            self._remove_service()

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_save_config(self) -> None:
        """Read all widget values and write config.json."""
        config = self._build_config()
        _save_config(config)
        self._config = config
        self.notify("✅ config.json saved!", severity="information")

    def _build_config(self) -> dict:
        """Collect values from all widgets into a config dict."""
        def _inp(id_: str) -> str:
            return self.query_one(f"#{id_}", Input).value.strip()

        def _sw(id_: str) -> bool:
            return self.query_one(f"#{id_}", Switch).value

        def _float(val: str, default: float) -> float:
            try:
                return float(val)
            except ValueError:
                return default

        def _int(val: str, default: int) -> int:
            try:
                return int(val)
            except ValueError:
                return default

        # Collect services from ListView
        svc_list = self.query_one("#svc-list", ListView)
        services = [
            item.query_one(Label).renderable
            for item in svc_list.query(ListItem)
        ]
        # Renderable might be a string or Text object
        services = [str(s) for s in services]

        return {
            "telegram_bot_token":    _inp("inp-token"),
            "telegram_chat_id":      _inp("inp-chat-id"),
            "device_name":           _inp("inp-device"),
            "temp_threshold_celsius": _float(_inp("inp-temp-thresh"), 75.0),
            "disk_threshold_percent": _int(_inp("inp-disk-thresh"), 85),
            "services_to_monitor":   services,
            "ip_notifier": {
                "enabled": _sw("sw-ip"),
            },
            "schedules": {
                "temp_monitor": {
                    "enabled":          _sw("sw-temp"),
                    "interval_minutes": _int(_inp("inp-temp-int"), 10),
                },
                "storage_watcher": {
                    "enabled":          _sw("sw-disk"),
                    "interval_minutes": _int(_inp("inp-disk-int"), 60),
                },
                "service_watchdog": {
                    "enabled":          _sw("sw-wd"),
                    "interval_minutes": _int(_inp("inp-wd-int"), 5),
                },
            },
        }

    def _add_service(self) -> None:
        inp = self.query_one("#inp-new-svc", Input)
        name = inp.value.strip()
        if not name:
            return
        svc_list = self.query_one("#svc-list", ListView)
        svc_list.append(ListItem(Label(name), id=f"svc-{name}"))
        inp.value = ""

    def _remove_service(self) -> None:
        svc_list = self.query_one("#svc-list", ListView)
        highlighted = svc_list.highlighted_child
        if highlighted:
            highlighted.remove()

    def _run_installer(self) -> None:
        """Run the installer in a background thread, logging output to the TUI."""
        # Switch to Apply tab so user can see the log
        try:
            tc = self.query_one(TabbedContent)
            tc.active = "tab-apply"
        except Exception:
            pass

        log: Log = self.query_one("#install-log", Log)
        log.clear()
        log.write_line("Starting installation…")

        def _worker():
            from tui.installer import run_full_install
            try:
                run_full_install(log_callback=lambda msg: self.call_from_thread(log.write_line, msg))
                self.call_from_thread(log.write_line, "✅ Installation complete!")
                self.call_from_thread(
                    self.notify, "Installation complete!", severity="information"
                )
            except Exception as e:
                self.call_from_thread(log.write_line, f"❌ Error: {e}")
                self.call_from_thread(
                    self.notify, f"Install failed: {e}", severity="error"
                )

        threading.Thread(target=_worker, daemon=True).start()
