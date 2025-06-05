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
from screens.create_footer_message_screen import CreateFooterMessageScreen


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
