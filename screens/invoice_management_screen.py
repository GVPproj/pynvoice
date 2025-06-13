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
from database import list_invoices, get_invoice_data
from screens.invoice_form_screen import InvoiceFormScreen
from screens.invoice_items_screen import AddInvoiceItemsScreen


class InvoiceManagementScreen(Screen):
    """Screen for managing invoices."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_invoice_id = None
        self.invoice_map = {}  # Maps ListItem index to invoice_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Invoice Management", classes="title"),
            Static(
                "(Create, edit, and manage invoices. Click an invoice to select it, then use buttons below.)"
            ),
            Horizontal(
                Button("New Invoice", variant="primary", id="create"),
                Button("Edit Invoice", variant="default", id="edit", disabled=True),
                Button("View Items", variant="default", id="view_items", disabled=True),
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
        self.invoice_map.clear()

        invoices = list_invoices()
        if invoices:
            for index, invoice_data in enumerate(invoices):
                # invoice_data: (id, sender_name, client_name, date_created, paid)
                invoice_id, sender_name, client_name, date_created, paid = invoice_data
                date_str = (
                    date_created.split()[0] if date_created else "Unknown"
                )  # Split on space and take first part (date only)
                paid_status = "✓ PAID" if paid else "○ UNPAID"
                display_text = f"Invoice #{invoice_id} | {sender_name} → {client_name} | {date_str} | {paid_status}"
                item = ListItem(Label(display_text))
                invoice_list.append(item)
                self.invoice_map[index] = invoice_id
        else:
            invoice_list.append(ListItem(Label("No invoices found.")))

    def on_list_view_selected(self) -> None:
        invoice_list = self.query_one("#invoice-list", ListView)
        selected_index = invoice_list.index
        if selected_index is not None and selected_index in self.invoice_map:
            self.selected_invoice_id = self.invoice_map[selected_index]
            # Enable the action buttons when an invoice is selected
            self.query_one("#edit", Button).disabled = False
            self.query_one("#view_items", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(InvoiceFormScreen())
        elif event.button.id == "edit":
            if self.selected_invoice_id:
                # Get full invoice data for editing
                invoice_data, _ = get_invoice_data(self.selected_invoice_id)
                if invoice_data:
                    self.app.push_screen(InvoiceFormScreen(invoice_data))
        elif event.button.id == "view_items":
            if self.selected_invoice_id:
                self.app.push_screen(AddInvoiceItemsScreen(self.selected_invoice_id))
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        self.refresh_invoices()
        # Reset selection when returning to this screen
        self.selected_invoice_id = None
        self.query_one("#edit", Button).disabled = True
        self.query_one("#view_items", Button).disabled = True

    def action_back(self):
        self.app.pop_screen()
