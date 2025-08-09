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
from screens.provider.provider_form import Provider_Form


class ProviderManagement(Screen):
    """Screen for managing senders."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def __init__(self):
        super().__init__()
        self.sender_data_map = {}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Add or Edit Provider", classes="title"),
            Horizontal(
                Button("New Provider", variant="primary", id="create"),
                Button("Back", variant="default", id="back"),
                classes="buttons-container",
            ),
            Static("Providers", classes="title"),
            ListView(id="sender-list"),
            classes="management-screen",
        )
        yield Footer()

    def on_mount(self):
        self.refresh_senders()

    def refresh_senders(self):
        sender_list = self.query_one("#sender-list", ListView)
        sender_list.clear()
        self.sender_data_map.clear()

        senders = list_senders()
        if senders:
            for sender_data in senders:
                display_text = f"{sender_data[1]} | {sender_data[2] or 'No Address'} | {sender_data[3] or 'No Email'} | {sender_data[4] or 'No Phone'}"
                item = ListItem(Label(display_text))
                self.sender_data_map[item] = sender_data
                sender_list.append(item)
        else:
            sender_list.append(ListItem(Label("No senders found.")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item in self.sender_data_map:
            self.app.push_screen(Provider_Form(self.sender_data_map[event.item]))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(Provider_Form())
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        # Refresh the list when returning from create screen
        self.refresh_senders()

    def action_back(self):
        self.app.pop_screen()
