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
from database import create_footer_message


class CreateFooterMessageScreen(Screen):
    """Screen for creating a new footer message."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Footer Message", classes="title"),
            Static("Please enter the footer message text below:"),
            Container(
                Label("Message:"),
                Input(placeholder="Enter footer message", id="message"),
                classes="field",
            ),
            Horizontal(
                Button("Create Message", variant="primary", id="create"),
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons-container",
            ),
            Static("", id="status"),
            classes="create-form",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.create_footer_message()
        elif event.button.id == "cancel":
            self.action_cancel()

    def create_footer_message(self):
        message = self.query_one("#message", Input).value.strip()

        try:
            if not message:
                self.query_one("#status", Static).update(
                    "Error: Footer message is required!"
                )
                return

            footer_id = create_footer_message(message)
            self.query_one("#status", Static).update(
                f"Footer message created successfully! (ID: {footer_id})"
            )
            # Clear the form
            self.query_one("#message", Input).value = ""
        except ValueError as e:
            self.query_one("#status", Static).update(f"Validation error: {e}")
        except Exception as e:
            self.query_one("#status", Static).update(f"Error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
