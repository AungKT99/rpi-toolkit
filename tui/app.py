"""
app.py — Root Textual application.
Entry point for the rpi-toolkit TUI.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding

from tui.screens.menu import MainMenuScreen
from tui.screens.dashboard import DashboardScreen
from tui.screens.config import ConfigScreen


class RpiToolkitApp(App):
    """The rpi-toolkit TUI application."""

    TITLE = "rpi-toolkit"
    SUB_TITLE = "Raspberry Pi 5 Monitor"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
    ]

    SCREENS = {
        "menu":      MainMenuScreen,
        "dashboard": DashboardScreen,
        "config":    ConfigScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("menu")


def main():
    app = RpiToolkitApp()
    app.run()


if __name__ == "__main__":
    main()
