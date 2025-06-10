from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
)
from textual.theme import Theme
from textual.binding import Binding
from database import (
    DB_FILE,
    init_db,
)

from screens.sender_management_screen import SenderManagementScreen
from screens.client_management_screen import ClientManagementScreen
from screens.footer_message_management_screen import FooterMessageManagementScreen
from screens.invoice_management_screen import InvoiceManagementScreen

arctic_theme = Theme(
    name="arctic",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#B48EAD",
    foreground="#D8DEE9",
    background="#2E3440",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)


class pynvoice(App):
    """Main PyNvoice application."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit Application"),
    ]

    def on_mount(self) -> None:
        # Register the theme
        # self.register_theme(arctic_theme)

        # Set the app's theme
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📄 pynvoice 📄", classes="title"),
            Static(" (Tab or click on an option below to continue) "),
            Container(
                Button("Invoices", variant="primary", id="invoice_management"),
                Button("Senders", variant="primary", id="sender_management"),
                Button("Clients", variant="primary", id="client_management"),
                Button("Footers", variant="primary", id="footer_management"),
                Button(
                    "Exit",
                    variant="default",
                    id="exit",
                    classes="defaultBtn",
                ),
                classes="buttons-container",
            ),
            classes="main-menu",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "invoice_management":
            self.push_screen(InvoiceManagementScreen())
        elif event.button.id == "sender_management":
            self.push_screen(SenderManagementScreen())
        elif event.button.id == "client_management":
            self.push_screen(ClientManagementScreen())
        elif event.button.id == "footer_management":
            self.push_screen(FooterMessageManagementScreen())
        elif event.button.id == "exit":
            self.exit()

    def action_quit(self):
        self.exit()


if __name__ == "__main__":
    import os

    # Ensure DB_FILE path is correctly handled if it's relative
    if not os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' not found. It will be created.")

    init_db()  # Initialize database schema if needed

    try:
        app = pynvoice()
        app.run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Application terminated.")
