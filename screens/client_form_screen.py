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
from database import create_client, update_client


class ClientFormScreen(Screen):
    """Screen for creating or editing a client."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, client_data=None):
        super().__init__()
        self.client_data = client_data
        self.is_editing = client_data is not None

    def compose(self) -> ComposeResult:
        title = "Edit Client" if self.is_editing else "Create New Client"
        yield Header()
        yield Container(
            Static(title, classes="title"),
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
                Button(
                    "Update Client" if self.is_editing else "Create Client",
                    variant="primary",
                    id="save",
                ),
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons-container",
            ),
            Static("", id="message"),
            classes="create-form",
        )
        yield Footer()

    def on_mount(self):
        if self.is_editing and self.client_data:
            # Populate fields with existing data
            self.query_one("#name", Input).value = self.client_data[1] or ""
            self.query_one("#address", Input).value = self.client_data[2] or ""
            self.query_one("#email", Input).value = self.client_data[3] or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.save_client()
        elif event.button.id == "cancel":
            self.action_cancel()

    def save_client(self):
        name = self.query_one("#name", Input).value.strip()
        address = self.query_one("#address", Input).value.strip() or None
        email = self.query_one("#email", Input).value.strip() or None

        try:
            if not name:
                self.query_one("#message", Static).update(
                    "Error: Client name is required!"
                )
                return

            if self.is_editing:
                client_id = update_client(self.client_data[0], name, address, email)
                self.query_one("#message", Static).update(
                    f"Client updated successfully! (ID: {client_id})"
                )
                # Give a moment to read the message, then go back
                self.set_timer(1.0, self.action_cancel)
            else:
                client_id = create_client(name, address, email)
                self.query_one("#message", Static).update(
                    f"Client created successfully! (ID: {client_id})"
                )
                # Clear the form for new creation
                self.query_one("#name", Input).value = ""
                self.query_one("#address", Input).value = ""
                self.query_one("#email", Input).value = ""
        except ValueError as e:
            self.query_one("#message", Static).update(f"Validation error: {e}")
        except Exception as e:
            self.query_one("#message", Static).update(f"Database error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
