"""
app.py — Root Textual application.
Entry point for the rpi-toolkit TUI.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding

from tui.screens.dashboard import DashboardScreen
from tui.screens.config import ConfigScreen


class RpiToolkitApp(App):
    """The rpi-toolkit TUI application."""

    TITLE = "rpi-toolkit"
    SUB_TITLE = "Raspberry Pi 5 Monitor"

    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        Binding("q",      "quit",              "Quit",    show=True),
        Binding("c",      "push_screen('config')",   "⚙ Config", show=True),
        Binding("d",      "push_screen('dashboard')", "📊 Dashboard", show=True),
    ]

    SCREENS = {
        "dashboard": DashboardScreen,
        "config":    ConfigScreen,
    }

    def on_mount(self) -> None:
        # Start on the dashboard
        self.push_screen("dashboard")


def main():
    app = RpiToolkitApp()
    app.run()


if __name__ == "__main__":
    main()
