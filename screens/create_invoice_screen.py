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
)
from textual.containers import Container, Horizontal
from database import list_senders, list_clients, list_footer_messages, create_invoice


class CreateInvoiceScreen(Screen):
    """Screen for creating a new invoice."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Invoice", classes="title"),
            Static("Select sender, client, and optionally a footer message:"),
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
            Horizontal(
                Button("Create Invoice", variant="primary", id="create"),
                Button("Back", variant="default", id="cancel"),
                classes="buttons-container",
            ),
            Static("", id="status"),
            classes="create-form",
        )
        yield Footer()

    def on_mount(self):
        self.populate_selects()

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
        footer_messages = self.get_footer_messages()
        footer_options = [("No footer message", None)] + [
            (f"{f[1][:30]}... (ID: {f[0]})", f[0]) for f in footer_messages
        ]
        footer_select.set_options(footer_options)

    def get_footer_messages(self):
        """Get all footer messages from database"""
        return list_footer_messages()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.create_invoice()
        elif event.button.id == "cancel":
            self.action_cancel()

    def create_invoice(self):
        sender_id = self.query_one("#sender_select", Select).value
        client_id = self.query_one("#client_select", Select).value
        footer_id = self.query_one("#footer_select", Select).value

        if sender_id is None:
            self.query_one("#status", Static).update("Error: Please select a sender!")
            return

        if client_id is None:
            self.query_one("#status", Static).update("Error: Please select a client!")
            return

        try:
            # Pass paid=False as default for new invoices created through this screen
            invoice_id = create_invoice(sender_id, client_id, footer_id, paid=False)
            self.query_one("#status", Static).update(
                f"Invoice created successfully! (ID: {invoice_id})"
            )
            # Switch to add items screen - import here to avoid circular import
            from screens.add_invoice_items_screen import AddInvoiceItemsScreen

            self.app.push_screen(AddInvoiceItemsScreen(invoice_id))
        except Exception as e:
            self.query_one("#status", Static).update(f"Error: {e}")

    def action_cancel(self):
        self.app.pop_screen()
