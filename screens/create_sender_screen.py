import sqlite3
from database import DB_FILE
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


class CreateSenderScreen(Screen):
    """Screen for creating a new sender."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Sender", classes="title"),
            Static("Please enter the sender's information below:"),
            Container(
                Label("Name:"),
                Input(placeholder="Enter sender name", id="name"),
                classes="field",
            ),
            Container(
                Label("Address:"),
                Input(placeholder="Enter sender address", id="address"),
                classes="field",
            ),
            Container(
                Label("Email:"),
                Input(placeholder="Enter sender email", id="email"),
                classes="field",
            ),
            Container(
                Label("Phone:"),
                Input(placeholder="Enter sender phone", id="phone"),
                classes="field",
            ),
            Horizontal(
                Button("Create Sender", variant="primary", id="create"),
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons-container",
            ),
            Static("", id="message"),
            classes="create-form",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.create_sender()
        elif event.button.id == "cancel":
            self.action_cancel()

    def create_sender(self):
        name = self.query_one("#name", Input).value.strip()
        address = self.query_one("#address", Input).value.strip()
        email = self.query_one("#email", Input).value.strip()
        phone = self.query_one("#phone", Input).value.strip()

        if not name:
            self.query_one("#message", Static).update("Error: Sender name is required!")
            return

        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "INSERT INTO sender (name, address, email, phone) VALUES (?, ?, ?, ?)",
                (name, address, email, phone),
            )
            conn.commit()
            conn.close()
            self.query_one("#message", Static).update("Sender created successfully!")
            # Clear the form
            self.query_one("#name", Input).value = ""
            self.query_one("#address", Input).value = ""
            self.query_one("#email", Input).value = ""
            self.query_one("#phone", Input).value = ""
        except sqlite3.Error as e:
            self.query_one("#message", Static).update(f"Database error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
