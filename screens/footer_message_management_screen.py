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
from database import list_footer_messages
from screens.footer_message_form_screen import FooterMessageFormScreen


class FooterMessageManagementScreen(Screen):
    """Screen for managing footer messages."""

    BINDINGS = [
        Binding("escape", "back", "Back to Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Add or Edit Invoice Footer Messages", classes="title"),
            Horizontal(
                Button("New Message", variant="primary", id="create"),
                Button("Back", variant="default", id="back"),
                classes="buttons-container",
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
                display_text = f"{footer_data[0]} | {truncated_message}"
                item = ListItem(Label(display_text))
                item.footer_data = footer_data
                footer_list.append(item)
        else:
            footer_list.append(ListItem(Label("No footer messages found.")))

    def get_footer_messages(self):
        """Get all footer messages from database"""
        return list_footer_messages()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if hasattr(event.item, "footer_data"):
            self.app.push_screen(FooterMessageFormScreen(event.item.footer_data))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.app.push_screen(FooterMessageFormScreen())
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self):
        self.refresh_footer_messages()

    def action_back(self):
        self.app.pop_screen()
