import sqlite3
from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    ListView,
    ListItem,
    Label,
)
from textual.containers import Container, Horizontal
from database import DB_FILE
from screens.create_invoice_screen import CreateInvoiceScreen
from screens.add_invoice_items_screen import AddInvoiceItemsScreen


class InvoiceManagementScreen(Screen):
    """Screen for managing invoices."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Invoice Management", classes="title"),
            Static("(Create and manage invoices)"),
            Horizontal(
                Button("New Invoice", variant="primary", id="create"),
                Button("Back", variant="default", id="back"),
                classes="buttons-container",
            ),
            ListView(id="invoice-list"),
            classes="management-screen",
        )
        yield Footer()

    def on_mount(self):
        self.refresh_invoices()

    def refresh_invoices(self):
        invoice_list = self.query_one("#invoice-list", ListView)
        invoice_list.clear()

        invoices = self.get_invoices()
        if invoices:
            for invoice_data in invoices:
                date_str = invoice_data[3].split()[
                    0
                ]  # Split on space and take first part (date only)
                display_text = f"Invoice #{invoice_data[0]} | Sender: {invoice_data[1]} | Client: {invoice_data[2]} | Date: {date_str}"
                item = ListItem(Label(display_text))
                item.invoice_data = invoice_data
                invoice_list.append(item)
        else:
            invoice_list.append(ListItem(Label("No invoices found.")))

    def get_invoices(self):
        """Get all invoices from database"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            """
            SELECT 
                i.id,
                s.name as sender_name,
                c.name as client_name,
                i.date_created
            FROM invoice i
            LEFT JOIN sender s ON i.sender_id = s.id
            LEFT JOIN client c ON i.client_id = c.id
            ORDER BY i.date_created DESC
        """
        )
        invoices = c.fetchall()
        conn.close()
        return invoices

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if hasattr(event.item, "invoice_data"):
            invoice_id = event.item.invoice_data[0]
            self.app.push_screen(AddInvoiceItemsScreen(invoice_id))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(CreateInvoiceScreen())
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        self.refresh_invoices()

    def action_back(self):
        self.app.pop_screen()
