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
)
from textual.screen import Screen
from textual.binding import Binding
from database import DB_FILE, init_db, list_senders, list_clients, create_client


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


class PyNvoiceApp(App):
    """Main PyNvoice application."""

    CSS_PATH = "styles.css"

    BINDINGS = [
        Binding("q", "quit", "Quit Application"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("PyNvoice Main Menu", classes="title"),
            Static("(Select an option below to continue)"),
            Container(
                Button("Sender Management", variant="primary", id="sender_management"),
                Button("Client Management", variant="primary", id="client_management"),
                Button("Exit Application", variant="default", id="exit"),
                classes="buttons",
            ),
            classes="main-menu",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "sender_management":
            self.push_screen(SenderManagementScreen())
        elif event.button.id == "client_management":
            self.push_screen(ClientManagementScreen())
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
