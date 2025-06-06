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
from database import list_senders
from screens.create_sender_screen import CreateSenderScreen
from screens.sender_detail_screen import SenderDetailScreen


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
