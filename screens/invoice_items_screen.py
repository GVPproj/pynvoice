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
    Input,
)
from textual.containers import Container, Horizontal
from database import add_invoice_item, get_invoice_data
from pdf_generator import generate_invoice_pdf


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
            Horizontal(
                Container(
                    Label("Quantity:"),
                    Input(placeholder="Enter quantity", id="amount"),
                    classes="field half-width",
                ),
                Container(
                    Label("Cost per Unit:"),
                    Input(placeholder="Enter cost per unit", id="cost_per_unit"),
                    classes="field half-width",
                ),
                classes="horizontal-fields",
            ),
            Horizontal(
                Button("Add Item", variant="primary", id="add_item"),
                Button("Generate PDF", variant="success", id="finish"),
                Button("Back", variant="default", id="cancel"),
                classes="buttons-container",
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
        _, items = get_invoice_data(self.invoice_id)

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
