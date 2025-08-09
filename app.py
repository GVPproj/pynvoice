from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
)
from textual.binding import Binding
from database import (
    DB_FILE,
    init_db,
)

from screens.sender_management_screen import SenderManagementScreen
from screens.client_management_screen import ClientManagementScreen
from screens.footer_message_management_screen import FooterMessageManagementScreen
from screens.invoice_management_screen import InvoiceManagementScreen


class pynvoice(App):
    """Main PyNvoice application."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit Application"),
    ]

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📄 pynvoice 📄", classes="title"),
            Static(
                "Tab or click on an option below. You might need to make your terminal window a bit bigger to enjoy the full experience.",
                classes="subtitle",
            ),
            Static(
                "To create invoices, you'll need at least one sender, and one client.",
                classes="subtitle",
            ),
            Container(
                Button("📄 Invoices", id="invoice_management", classes="menu-option"),
                Button("👤 Senders", id="sender_management", classes="menu-option"),
                Button("🏢 Clients", id="client_management", classes="menu-option"),
                Button("💬 Messages", id="footer_management", classes="menu-option"),
                Button(
                    "🚪 Exit",
                    id="exit",
                    classes="menu-option exit-option",
                ),
                # classes="buttons-container",
            ),
            classes="main-menu",
        )
        yield Footer()

    def on_button_pressed(self, event) -> None:
        """Handle button presses on menu options."""
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

    def on_click(self, event) -> None:
        """Handle mouse clicks on menu options (fallback for any remaining static elements)."""
        if hasattr(event.widget, "id"):
            if event.widget.id == "invoice_management":
                self.push_screen(InvoiceManagementScreen())
            elif event.widget.id == "sender_management":
                self.push_screen(SenderManagementScreen())
            elif event.widget.id == "client_management":
                self.push_screen(ClientManagementScreen())
            elif event.widget.id == "footer_management":
                self.push_screen(FooterMessageManagementScreen())
            elif event.widget.id == "exit":
                self.exit()

    async def action_quit(self) -> None:
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
        print("I hope you enjoyed your pynvoice session.  Take care!")
