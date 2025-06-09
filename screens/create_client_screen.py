from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    Label,
    Input,
)
from textual.containers import Container, Horizontal
from database import create_client


class CreateClientScreen(Screen):
    """Screen for creating a new client."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Client", classes="title"),
            Static("Please enter the client's details below:"),
            Static("(Name is required, Address and Email are optional)"),
            Container(
                Label("Name *:"),
                Input(placeholder="Enter client name", id="name"),
                classes="field",
            ),
            Container(
                Label("Address (optional):"),
                Input(placeholder="Enter client address", id="address"),
                classes="field",
            ),
            Container(
                Label("Email (optional):"),
                Input(placeholder="Enter client email", id="email"),
                classes="field",
            ),
            Horizontal(
                Button("Create Client", variant="primary", id="create"),
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons-container",
            ),
            Static("", id="message"),
            classes="create-form",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.create_client()
        elif event.button.id == "cancel":
            self.action_cancel()

    def create_client(self):
        name = self.query_one("#name", Input).value.strip()
        address = self.query_one("#address", Input).value.strip() or None
        email = self.query_one("#email", Input).value.strip() or None

        try:
            if not name:
                self.query_one("#message", Static).update(
                    "Error: Client name is required!"
                )
                return

            client_id = create_client(name, address, email)
            self.query_one("#message", Static).update(
                f"Client created successfully! (ID: {client_id})"
            )
            # Clear the form
            self.query_one("#name", Input).value = ""
            self.query_one("#address", Input).value = ""
            self.query_one("#email", Input).value = ""
        except ValueError as e:
            self.query_one("#message", Static).update(f"Validation error: {e}")
        except Exception as e:
            self.query_one("#message", Static).update(f"Database error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
