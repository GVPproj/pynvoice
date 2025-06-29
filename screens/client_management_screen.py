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
from database import list_clients
from screens.client_form_screen import ClientFormScreen


class ClientManagementScreen(Screen):
    """Screen for managing clients."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Add or Edit Clients", classes="title"),
            Horizontal(
                Button("New Client", variant="primary", id="create"),
                Button("Back", variant="default", id="back"),
                classes="buttons-container",
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
                display_text = f"{client_data[1]} | Addr: {address_display} | Email: {email_display}"
                item = ListItem(Label(display_text))
                item.client_data = client_data
                client_list.append(item)
        else:
            client_list.append(ListItem(Label("No clients found.")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if hasattr(event.item, "client_data"):
            self.app.push_screen(ClientFormScreen(event.item.client_data))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(ClientFormScreen())
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        # Refresh the list when returning from create screen
        self.refresh_clients()

    def action_back(self):
        self.app.pop_screen()
