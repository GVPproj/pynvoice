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
from database import create_sender, update_sender


class Provider_Form(Screen):
    """Screen for creating or editing a provider."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, provider_data=None):
        super().__init__()
        self.provider_data = provider_data
        self.is_editing = provider_data is not None

    def compose(self) -> ComposeResult:
        title = "Edit Provider" if self.is_editing else "Create New Provider"
        yield Header()
        yield Container(
            Static(title, classes="title"),
            Container(
                Label("Name:"),
                Input(placeholder="Enter provider name", id="name"),
                classes="field",
            ),
            Container(
                Label("Address:"),
                Input(placeholder="Enter provider address", id="address"),
                classes="field",
            ),
            Horizontal(
                Container(
                    Label("Email:"),
                    Input(placeholder="Enter provider email", id="email"),
                    classes="field half-width",
                ),
                Container(
                    Label("Phone:"),
                    Input(placeholder="Enter provider phone", id="phone"),
                    classes="field half-width",
                ),
                classes="horizontal-fields",
            ),
            Horizontal(
                Button(
                    "Update" if self.is_editing else "Create",
                    variant="primary",
                    id="save",
                ),
                Button("Back", variant="default", id="cancel"),
                classes="buttons-container",
            ),
            Static("", id="message"),
            classes="create-form",
        )
        yield Footer()

    def on_mount(self):
        if self.is_editing and self.provider_data:
            # Populate fields with existing data
            self.query_one("#name", Input).value = self.provider_data[1] or ""
            self.query_one("#address", Input).value = self.provider_data[2] or ""
            self.query_one("#email", Input).value = self.provider_data[3] or ""
            self.query_one("#phone", Input).value = self.provider_data[4] or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.save_provider()
        elif event.button.id == "cancel":
            self.action_cancel()

    def save_provider(self):
        name = self.query_one("#name", Input).value.strip()
        address = self.query_one("#address", Input).value.strip() or None
        email = self.query_one("#email", Input).value.strip() or None
        phone = self.query_one("#phone", Input).value.strip() or None

        try:
            if not name:
                self.query_one("#message", Static).update(
                    "Error: Provider name is required!"
                )
                return

            if self.is_editing and self.provider_data:
                provider_id = update_sender(
                    self.provider_data[0], name, address, email, phone
                )
                self.query_one("#message", Static).update(
                    f"Provider updated successfully! (ID: {provider_id})"
                )
                # Give a moment to read the message, then go back
                self.set_timer(1.0, self.action_cancel)
            else:
                provider_id = create_sender(name, address, email, phone)
                self.query_one("#message", Static).update(
                    f"Provider created successfully! (ID: {provider_id})"
                )
                # Clear the form for new creation
                self.query_one("#name", Input).value = ""
                self.query_one("#address", Input).value = ""
                self.query_one("#email", Input).value = ""
                self.query_one("#phone", Input).value = ""
        except ValueError as e:
            self.query_one("#message", Static).update(f"Validation error: {e}")
        except Exception as e:
            self.query_one("#message", Static).update(f"Database error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
