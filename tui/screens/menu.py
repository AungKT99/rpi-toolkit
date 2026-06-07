"""
menu.py — Main menu screen.
Arrow keys to navigate, Enter to select, Q to quit.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, ListItem, ListView, Static


class MainMenuScreen(Screen):
    """Entry point — navigable main menu."""

    BINDINGS = [("q", "app.quit", "Quit")]

    DEFAULT_CSS = """
    MainMenuScreen {
        align: center middle;
    }

    #menu-box {
        width: 40;
        height: auto;
        border: double $accent;
        padding: 1 2;
        background: $surface;
    }

    #menu-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
        width: 100%;
    }

    #menu-subtitle {
        text-align: center;
        color: $text-muted;
        padding-bottom: 1;
        width: 100%;
    }

    ListView {
        background: $surface;
        border: none;
        padding: 0;
    }

    ListItem {
        padding: 0 1;
        height: 2;
    }

    ListItem > Label {
        width: 100%;
        padding: 0 1;
    }

    ListView > ListItem.--highlight {
        background: $accent;
        color: $background;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        from textual.containers import Vertical
        with Vertical(id="menu-box"):
            yield Label("🍓  rpi-toolkit", id="menu-title")
            yield Label("Raspberry Pi 5 Monitor", id="menu-subtitle")
            yield ListView(
                ListItem(Label("📊   Dashboard"),     id="item-dashboard"),
                ListItem(Label("⚙    Configuration"), id="item-config"),
                ListItem(Label("✕    Quit"),           id="item-quit"),
                id="main-menu",
            )

        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id == "item-dashboard":
            self.app.push_screen("dashboard")
        elif item_id == "item-config":
            self.app.push_screen("config")
        elif item_id == "item-quit":
            self.app.exit()
