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
from database import create_footer_message, update_footer_message


class FooterMessageFormScreen(Screen):
    """Screen for creating or editing a footer message."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, footer_data=None):
        super().__init__()
        self.footer_data = footer_data
        self.is_editing = footer_data is not None

    def compose(self) -> ComposeResult:
        title = (
            "Edit Footer Message" if self.is_editing else "Create New Footer Message"
        )
        yield Header()
        yield Container(
            Static(title, classes="title"),
            Static("Please enter the footer message text below:"),
            Container(
                Label("Message:"),
                Input(placeholder="Enter footer message", id="message"),
                classes="field",
            ),
            Horizontal(
                Button(
                    "Update Message" if self.is_editing else "Create Message",
                    variant="primary",
                    id="save",
                ),
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons-container",
            ),
            Static("", id="status"),
            classes="create-form",
        )
        yield Footer()

    def on_mount(self):
        if self.is_editing and self.footer_data:
            # Populate field with existing data
            self.query_one("#message", Input).value = self.footer_data[1] or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.save_footer_message()
        elif event.button.id == "cancel":
            self.action_cancel()

    def save_footer_message(self):
        message = self.query_one("#message", Input).value.strip()

        try:
            if not message:
                self.query_one("#status", Static).update(
                    "Error: Footer message is required!"
                )
                return

            if self.is_editing:
                footer_id = update_footer_message(self.footer_data[0], message)
                self.query_one("#status", Static).update(
                    f"Footer message updated successfully! (ID: {footer_id})"
                )
                # Give a moment to read the message, then go back
                self.set_timer(1.0, self.action_cancel)
            else:
                footer_id = create_footer_message(message)
                self.query_one("#status", Static).update(
                    f"Footer message created successfully! (ID: {footer_id})"
                )
                # Clear the form for new creation
                self.query_one("#message", Input).value = ""
        except ValueError as e:
            self.query_one("#status", Static).update(f"Validation error: {e}")
        except Exception as e:
            self.query_one("#status", Static).update(f"Error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
