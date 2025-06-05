from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
)
from textual.containers import Container


class SenderDetailScreen(Screen):
    """Screen for displaying sender details."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, sender_data):
        super().__init__()
        self.sender_data = sender_data

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Selected Sender: {self.sender_data[1]}", classes="title"),
            Static(f"ID: {self.sender_data[0]}"),
            Static(f"Name: {self.sender_data[1]}"),
            Static(f"Address: {self.sender_data[2]}"),
            Static(f"Email: {self.sender_data[3]}"),
            Static(f"Phone: {self.sender_data[4]}"),
            Static(""),
            Static("This sender is now notionally selected."),
            Static(
                "(In a full app, you might proceed to create an invoice with this sender.)"
            ),
            Static(""),
            Button("Back to Menu", variant="primary", id="back"),
            classes="detail-view",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_back()

    def action_back(self):
        self.app.pop_screen()
