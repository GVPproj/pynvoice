import sqlite3
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    ListView,
    ListItem,
    Label,
    Input,
    Select,
)
from textual.theme import Theme


from textual.screen import Screen
from textual.binding import Binding
from database import (
    DB_FILE,
    init_db,
    list_senders,
    list_clients,
    list_footer_messages,
    create_client,
    create_sender,
    create_footer_message,
    create_invoice,
    add_invoice_item,
    get_invoice_data,
)
from pdf_generator import generate_invoice_pdf

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


class CreateSenderScreen(Screen):
    """Screen for creating a new sender."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Sender", classes="title"),
            Static("Please enter the sender's details below:"),
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
                classes="buttons",
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


class CreateClientScreen(Screen):
    """Screen for creating a new client."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Client", classes="title"),
            Static("Please enter the client's details below:"),
            Static("(Name is required, Address and Email are optional)"),
            Container(
                Label("Name *:"),
                Input(placeholder="Enter client name", id="name"),
                classes="field",
            ),
            Container(
                Label("Address (optional):"),
                Input(placeholder="Enter client address", id="address"),
                classes="field",
            ),
            Container(
                Label("Email (optional):"),
                Input(placeholder="Enter client email", id="email"),
                classes="field",
            ),
            Horizontal(
                Button("Create Client", variant="primary", id="create"),
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons",
            ),
            Static("", id="message"),
            classes="create-form",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.create_client()
        elif event.button.id == "cancel":
            self.action_cancel()

    def create_client(self):
        name = self.query_one("#name", Input).value.strip()
        address = self.query_one("#address", Input).value.strip() or None
        email = self.query_one("#email", Input).value.strip() or None

        try:
            if not name:
                self.query_one("#message", Static).update(
                    "Error: Client name is required!"
                )
                return

            client_id = create_client(name, address, email)
            self.query_one("#message", Static).update(
                f"Client created successfully! (ID: {client_id})"
            )
            # Clear the form
            self.query_one("#name", Input).value = ""
            self.query_one("#address", Input).value = ""
            self.query_one("#email", Input).value = ""
        except ValueError as e:
            self.query_one("#message", Static).update(f"Validation error: {e}")
        except sqlite3.Error as e:
            self.query_one("#message", Static).update(f"Database error: {e}")

    def action_cancel(self):
        self.app.pop_screen()


class SenderDetailScreen(Screen):
    """Screen for displaying sender details."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, sender_data):
        super().__init__()
        self.sender_data = sender_data

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Selected Sender: {self.sender_data[1]}", classes="title"),
            Static(f"ID: {self.sender_data[0]}"),
            Static(f"Name: {self.sender_data[1]}"),
            Static(f"Address: {self.sender_data[2]}"),
            Static(f"Email: {self.sender_data[3]}"),
            Static(f"Phone: {self.sender_data[4]}"),
            Static(""),
            Static("This sender is now notionally selected."),
            Static(
                "(In a full app, you might proceed to create an invoice with this sender.)"
            ),
            Static(""),
            Button("Back to Menu", variant="primary", id="back"),
            classes="detail-view",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_back()

    def action_back(self):
        self.app.pop_screen()


class ClientDetailScreen(Screen):
    """Screen for displaying client details."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, client_data):
        super().__init__()
        self.client_data = client_data

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Selected Client: {self.client_data[1]}", classes="title"),
            Static(f"ID: {self.client_data[0]}"),
            Static(f"Name: {self.client_data[1]}"),
            Static(
                f"Address: {self.client_data[2] if self.client_data[2] else 'Not provided'}"
            ),
            Static(
                f"Email: {self.client_data[3] if self.client_data[3] else 'Not provided'}"
            ),
            Static(""),
            Static("This client is now notionally selected."),
            Static(
                "(In a full app, you might proceed to create an invoice for this client.)"
            ),
            Static(""),
            Button("Back to Menu", variant="primary", id="back"),
            classes="detail-view",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_back()

    def action_back(self):
        self.app.pop_screen()


class SenderManagementScreen(Screen):
    """Screen for managing senders."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Sender Management", classes="title"),
            Static("(Select a sender to view details, or create a new one)"),
            Horizontal(
                Button("Create New Sender", variant="primary", id="create"),
                Button("Back to Main Menu", variant="default", id="back"),
                classes="buttons",
            ),
            ListView(id="sender-list"),
            classes="management-screen",
        )
        yield Footer()

    def on_mount(self):
        self.refresh_senders()

    def refresh_senders(self):
        sender_list = self.query_one("#sender-list", ListView)
        sender_list.clear()

        senders = list_senders()
        if senders:
            for sender_data in senders:
                display_text = f"{sender_data[1]} (ID: {sender_data[0]}) | Addr: {sender_data[2]} | Email: {sender_data[3]} | Phone: {sender_data[4]}"
                item = ListItem(Label(display_text))
                item.sender_data = sender_data
                sender_list.append(item)
        else:
            sender_list.append(ListItem(Label("No senders found.")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if hasattr(event.item, "sender_data"):
            self.app.push_screen(SenderDetailScreen(event.item.sender_data))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(CreateSenderScreen())
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        # Refresh the list when returning from create screen
        self.refresh_senders()

    def action_back(self):
        self.app.pop_screen()


class ClientManagementScreen(Screen):
    """Screen for managing clients."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Client Management", classes="title"),
            Static("(Select a client to view details, or create a new one)"),
            Horizontal(
                Button("Create New Client", variant="primary", id="create"),
                Button("Back to Main Menu", variant="default", id="back"),
                classes="buttons",
            ),
            ListView(id="client-list"),
            classes="management-screen",
        )
        yield Footer()

    def on_mount(self):
        self.refresh_clients()

    def refresh_clients(self):
        client_list = self.query_one("#client-list", ListView)
        client_list.clear()

        clients = list_clients()
        if clients:
            for client_data in clients:
                address_display = client_data[2] if client_data[2] else "N/A"
                email_display = client_data[3] if client_data[3] else "N/A"
                display_text = f"{client_data[1]} (ID: {client_data[0]}) | Addr: {address_display} | Email: {email_display}"
                item = ListItem(Label(display_text))
                item.client_data = client_data
                client_list.append(item)
        else:
            client_list.append(ListItem(Label("No clients found.")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if hasattr(event.item, "client_data"):
            self.app.push_screen(ClientDetailScreen(event.item.client_data))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(CreateClientScreen())
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        # Refresh the list when returning from create screen
        self.refresh_clients()

    def action_back(self):
        self.app.pop_screen()


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
                classes="buttons",
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


class FooterMessageManagementScreen(Screen):
    """Screen for managing footer messages."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Footer Message Management", classes="title"),
            Static("(Manage footer messages for invoices)"),
            Horizontal(
                Button("Create New Message", variant="primary", id="create"),
                Button("Back to Main Menu", variant="default", id="back"),
                classes="buttons",
            ),
            ListView(id="footer-list"),
            classes="management-screen",
        )
        yield Footer()

    def on_mount(self):
        self.refresh_footer_messages()

    def refresh_footer_messages(self):
        footer_list = self.query_one("#footer-list", ListView)
        footer_list.clear()

        footer_messages = list_footer_messages()
        if footer_messages:
            for footer_data in footer_messages:
                # Truncate long messages for display
                truncated_message = (
                    footer_data[1][:50] + "..."
                    if len(footer_data[1]) > 50
                    else footer_data[1]
                )
                display_text = f"ID: {footer_data[0]} | {truncated_message}"
                item = ListItem(Label(display_text))
                item.footer_data = footer_data
                footer_list.append(item)
        else:
            footer_list.append(ListItem(Label("No footer messages found.")))

    def get_footer_messages(self):
        """Get all footer messages from database"""
        return list_footer_messages()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(CreateFooterMessageScreen())
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        self.refresh_footer_messages()

    def action_back(self):
        self.app.pop_screen()


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
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons",
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
            invoice_id = create_invoice(sender_id, client_id, footer_id)
            self.query_one("#status", Static).update(
                f"Invoice created successfully! (ID: {invoice_id})"
            )
            # Switch to add items screen
            self.app.push_screen(AddInvoiceItemsScreen(invoice_id))
        except Exception as e:
            self.query_one("#status", Static).update(f"Error: {e}")

    def action_cancel(self):
        self.app.pop_screen()


class AddInvoiceItemsScreen(Screen):
    """Screen for adding items to an invoice."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, invoice_id):
        super().__init__()
        self.invoice_id = invoice_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Add Items to Invoice #{self.invoice_id}", classes="title"),
            Static("Add items to your invoice below:"),
            Container(
                Label("Item Name:"),
                Input(placeholder="Enter item name", id="item_name"),
                classes="field",
            ),
            Container(
                Label("Quantity:"),
                Input(placeholder="Enter quantity", id="amount"),
                classes="field",
            ),
            Container(
                Label("Cost per Unit:"),
                Input(placeholder="Enter cost per unit", id="cost_per_unit"),
                classes="field",
            ),
            Horizontal(
                Button("Add Item", variant="primary", id="add_item"),
                Button("Finish & Generate PDF", variant="success", id="finish"),
                Button("Cancel", variant="default", id="cancel"),
                classes="buttons",
            ),
            Static("", id="status"),
            Static("Items added:", classes="section-title"),
            ListView(id="items-list"),
            classes="create-form",
        )
        yield Footer()

    def on_mount(self):
        self.refresh_items()

    def refresh_items(self):
        items_list = self.query_one("#items-list", ListView)
        items_list.clear()

        # Get current items for this invoice
        invoice_data, items = get_invoice_data(self.invoice_id)

        if items:
            for item in items:
                item_name, amount, cost_per_unit = item
                total_cost = amount * cost_per_unit
                display_text = f"{item_name} | Qty: {amount} | Cost: ${cost_per_unit:.2f} | Total: ${total_cost:.2f}"
                items_list.append(ListItem(Label(display_text)))
        else:
            items_list.append(ListItem(Label("No items added yet.")))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_item":
            self.add_item()
        elif event.button.id == "finish":
            self.finish_invoice()
        elif event.button.id == "cancel":
            self.action_back()

    def add_item(self):
        item_name = self.query_one("#item_name", Input).value.strip()
        amount_str = self.query_one("#amount", Input).value.strip()
        cost_str = self.query_one("#cost_per_unit", Input).value.strip()

        try:
            if not item_name:
                self.query_one("#status", Static).update(
                    "Error: Item name is required!"
                )
                return

            amount = float(amount_str)
            cost_per_unit = float(cost_str)

            if amount <= 0:
                self.query_one("#status", Static).update(
                    "Error: Quantity must be positive!"
                )
                return

            if cost_per_unit <= 0:
                self.query_one("#status", Static).update(
                    "Error: Cost per unit must be positive!"
                )
                return

            add_invoice_item(self.invoice_id, item_name, amount, cost_per_unit)
            self.query_one("#status", Static).update("Item added successfully!")

            # Clear form
            self.query_one("#item_name", Input).value = ""
            self.query_one("#amount", Input).value = ""
            self.query_one("#cost_per_unit", Input).value = ""

            # Refresh the items list
            self.refresh_items()

        except ValueError:
            self.query_one("#status", Static).update(
                "Error: Please enter valid numbers for quantity and cost!"
            )
        except Exception as e:
            self.query_one("#status", Static).update(f"Error: {e}")

    def finish_invoice(self):
        try:
            # Generate PDF
            filename = generate_invoice_pdf(self.invoice_id)
            self.query_one("#status", Static).update(
                f"Invoice PDF generated: {filename}"
            )
        except Exception as e:
            self.query_one("#status", Static).update(f"Error generating PDF: {e}")

    def action_back(self):
        self.app.pop_screen()


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
                Button("Create New Invoice", variant="primary", id="create"),
                Button("Back to Main Menu", variant="default", id="back"),
                classes="buttons",
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
                display_text = f"Invoice #{invoice_data[0]} | Sender: {invoice_data[1]} | Client: {invoice_data[2]} | Date: {invoice_data[3]}"
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


class PyNvoiceApp(App):
    """Main PyNvoice application."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit Application"),
    ]

    def on_mount(self) -> None:
        # Register the theme
        self.register_theme(arctic_theme)

        # Set the app's theme
        self.theme = "arctic"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📄 pynvoice 📄", classes="title"),
            Static(" (Tab or click on an option below to continue) "),
            Container(
                Button(
                    "Invoice Management", variant="primary", id="invoice_management"
                ),
                Button("Sender Management", variant="primary", id="sender_management"),
                Button("Client Management", variant="primary", id="client_management"),
                Button("Footer Messages", variant="primary", id="footer_management"),
                Button("Exit Application", variant="default", id="exit"),
                classes="buttons",
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
        app = PyNvoiceApp()
        app.run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Application terminated.")
