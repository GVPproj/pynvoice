from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    Label,
    Select,
    Switch,
)
from textual.containers import Container, Horizontal
from database import (
    list_senders,
    list_clients,
    list_footer_messages,
    create_invoice,
    update_invoice,
)


class InvoiceFormScreen(Screen):
    """Screen for creating or editing an invoice."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, invoice_data=None):
        super().__init__()
        self.invoice_data = invoice_data
        self.is_editing = invoice_data is not None

    def compose(self) -> ComposeResult:
        title = "Edit Invoice" if self.is_editing else "Create New Invoice"
        yield Header()
        yield Container(
            Static(title, classes="title"),
            Container(
                Label("Sender:"),
                Select(
                    prompt="Choose a sender",
                    options=[],
                    id="sender_select",
                ),
                classes="field",
            ),
            Container(
                Label("Client:"),
                Select(
                    prompt="Choose a client",
                    options=[],
                    id="client_select",
                ),
                classes="field",
            ),
            Container(
                Label("Footer Message (Optional):"),
                Select(
                    prompt="Choose a footer message",
                    options=[],
                    id="footer_select",
                ),
                classes="field",
            ),
            Container(
                Label("Paid Status:"),
                Switch(value=False, id="paid_switch"),
                classes="field",
            ),
            Horizontal(
                Button(
                    "Update Invoice" if self.is_editing else "Create Invoice",
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
        self.populate_selects()
        if self.is_editing and self.invoice_data:
            self.populate_fields()

    def populate_selects(self):
        # Populate senders
        sender_select = self.query_one("#sender_select", Select)
        senders = list_senders()
        sender_options = [(f"{s[1]} (ID: {s[0]})", s[0]) for s in senders]
        sender_select.set_options(sender_options)

        # Populate clients
        client_select = self.query_one("#client_select", Select)
        clients = list_clients()
        client_options = [(f"{c[1]} (ID: {c[0]})", c[0]) for c in clients]
        client_select.set_options(client_options)

        # Populate footer messages
        footer_select = self.query_one("#footer_select", Select)
        footer_messages = list_footer_messages()
        footer_options = [("No footer message", None)] + [
            (f"{f[1][:30]}... (ID: {f[0]})", f[0]) for f in footer_messages
        ]
        footer_select.set_options(footer_options)

    def populate_fields(self):
        """Populate form fields with existing invoice data"""
        if not self.invoice_data:
            return

        # Invoice data structure: (id, date_created, paid, sender_name, sender_address, sender_email, sender_phone,
        #                         client_name, client_address, client_email, footer_message, sender_id, client_id, footer_message_id)

        sender_id = self.invoice_data[11]
        client_id = self.invoice_data[12]
        footer_message_id = self.invoice_data[13]
        paid = self.invoice_data[2]

        # Set sender
        sender_select = self.query_one("#sender_select", Select)
        sender_select.value = sender_id

        # Set client
        client_select = self.query_one("#client_select", Select)
        client_select.value = client_id

        # Set footer message
        footer_select = self.query_one("#footer_select", Select)
        footer_select.value = footer_message_id

        # Set paid status
        paid_switch = self.query_one("#paid_switch", Switch)
        paid_switch.value = bool(paid)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.save_invoice()
        elif event.button.id == "cancel":
            self.action_cancel()

    def save_invoice(self):
        sender_id = self.query_one("#sender_select", Select).value
        client_id = self.query_one("#client_select", Select).value
        footer_id = self.query_one("#footer_select", Select).value
        paid = self.query_one("#paid_switch", Switch).value

        if sender_id is None:
            self.query_one("#message", Static).update("Error: Please select a sender!")
            return

        if client_id is None:
            self.query_one("#message", Static).update("Error: Please select a client!")
            return

        try:
            if self.is_editing:
                invoice_id = update_invoice(
                    self.invoice_data[0], sender_id, client_id, footer_id, paid
                )
                self.query_one("#message", Static).update(
                    f"Invoice updated successfully! (ID: {invoice_id})"
                )
                # Give a moment to read the message, then go back
                self.set_timer(1.0, self.action_cancel)
            else:
                invoice_id = create_invoice(sender_id, client_id, footer_id, paid)
                self.query_one("#message", Static).update(
                    f"Invoice created successfully! (ID: {invoice_id})"
                )
                # Switch to add items screen - import here to avoid circular import
                from screens.invoice_items_screen import AddInvoiceItemsScreen

                self.app.push_screen(AddInvoiceItemsScreen(invoice_id))
        except Exception as e:
            self.query_one("#message", Static).update(f"Error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
