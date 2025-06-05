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


class ClientDetailScreen(Screen):
    """Screen for displaying client details."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, client_data):
        super().__init__()
        self.client_data = client_data

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Selected Client: {self.client_data[1]}", classes="title"),
            Static(f"ID: {self.client_data[0]}"),
            Static(f"Name: {self.client_data[1]}"),
            Static(
                f"Address: {self.client_data[2] if self.client_data[2] else 'Not provided'}"
            ),
            Static(
                f"Email: {self.client_data[3] if self.client_data[3] else 'Not provided'}"
            ),
            Static(""),
            Static("This client is now notionally selected."),
            Static(
                "(In a full app, you might proceed to create an invoice for this client.)"
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
