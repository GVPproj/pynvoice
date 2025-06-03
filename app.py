import sqlite3
import os
import curses
from database import DB_FILE, init_db, list_senders


def create_sender_curses(stdscr):
    """Handles creation of a new sender using curses for I/O."""
    curses.echo()  # Enable echoing of input characters
    stdscr.clear()
    stdscr.addstr(0, 0, "--- Create New Sender ---")
    stdscr.addstr(1, 0, "Please enter the sender's details below:")

    details = {}
    prompts = [("Name", 3, 0), ("Address", 4, 0), ("Email", 5, 0), ("Phone", 6, 0)]

    for prompt_text, y, x_label in prompts:
        stdscr.addstr(y, x_label, f"{prompt_text}: ")
        stdscr.refresh()
        # Move cursor to input position
        input_val = (
            stdscr.getstr(y, x_label + len(prompt_text) + 2).decode("utf-8").strip()
        )
        details[prompt_text.lower()] = input_val

    curses.noecho()  # Disable echoing

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO sender (name, address, email, phone) VALUES (?, ?, ?, ?)",
            (details["name"], details["address"], details["email"], details["phone"]),
        )
        conn.commit()
        stdscr.addstr(len(prompts) + 3, 0, "Sender created successfully!")
    except sqlite3.Error as e:
        stdscr.addstr(len(prompts) + 3, 0, f"Database error: {e}")
    finally:
        conn.close()

    stdscr.addstr(len(prompts) + 4, 0, "Press any key to continue...")
    stdscr.refresh()
    stdscr.getch()


def run_app(stdscr):
    """Main application function using curses."""
    curses.curs_set(0)  # Hide the cursor
    stdscr.keypad(True)  # Enable special keys like arrow keys

    # Optional: Initialize color pairs if you want to use colors
    curses.start_color()
    curses.use_default_colors()
    # curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # Example: highlighted item

    current_selection_idx = 0

    while True:
        stdscr.clear()
        senders = list_senders()

        # Menu Title
        stdscr.addstr(0, 0, "--- PyNvoice Sender Management ---")
        stdscr.addstr(
            1, 0, "(Use UP/DOWN arrows to navigate, ENTER to select, 'q' to quit)"
        )

        menu_items = []

        header_y = 3
        if senders:
            stdscr.addstr(header_y, 0, "Existing Senders:")
            for sender_data in senders:
                # sender_data is (id, name, address, email, phone)
                display_text = f"{sender_data[1]} (ID: {sender_data[0]}) | Addr: {sender_data[2]} | Email: {sender_data[3]} | Phone: {sender_data[4]}"
                menu_items.append(
                    {"type": "sender", "data": sender_data, "display": display_text}
                )
            items_start_y = header_y + 1
        else:
            stdscr.addstr(header_y, 0, "No senders found.")
            items_start_y = header_y + 1
            # Adjust items_start_y if "No senders found" message is the only thing before options

        # Action items
        menu_items.append(
            {"type": "action", "data": "create", "display": "Create New Sender"}
        )
        menu_items.append(
            {"type": "action", "data": "exit", "display": "Exit Application"}
        )

        for idx, item in enumerate(menu_items):
            y_pos = items_start_y + idx
            display_str = item["display"]

            # Ensure we don't try to write past screen boundaries
            if y_pos >= curses.LINES - 1:  # curses.LINES gives terminal height
                stdscr.addstr(curses.LINES - 1, 0, "Too many items to display!")
                break

            if idx == current_selection_idx:
                stdscr.attron(curses.A_REVERSE)  # Highlight selected item
                stdscr.addstr(y_pos, 2, f"> {display_str_truncated(display_str, 4)}")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y_pos, 2, f"  {display_str_truncated(display_str, 4)}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_selection_idx = (current_selection_idx - 1 + len(menu_items)) % len(
                menu_items
            )
        elif key == curses.KEY_DOWN:
            current_selection_idx = (current_selection_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:  # 10 is LF, 13 is CR
            if not menu_items:  # Should not happen if Exit is always an option
                continue

            selected_option = menu_items[current_selection_idx]

            if selected_option["type"] == "sender":
                sender = selected_option["data"]
                stdscr.clear()
                stdscr.addstr(0, 0, f"--- Selected Sender: {sender[1]} ---")
                stdscr.addstr(2, 0, f"ID: {sender[0]}")
                stdscr.addstr(3, 0, f"Name: {sender[1]}")
                stdscr.addstr(4, 0, f"Address: {sender[2]}")
                stdscr.addstr(5, 0, f"Email: {sender[3]}")
                stdscr.addstr(6, 0, f"Phone: {sender[4]}")
                stdscr.addstr(8, 0, "This sender is now notionally selected.")
                stdscr.addstr(
                    9,
                    0,
                    "(In a full app, you might proceed to create an invoice with this sender.)",
                )
                stdscr.addstr(11, 0, "Press any key to return to the menu.")
                stdscr.refresh()
                stdscr.getch()
            elif selected_option["data"] == "create":
                create_sender_curses(stdscr)
                current_selection_idx = 0  # Reset selection to top after creation
            elif selected_option["data"] == "exit":
                break  # Exit the while True loop

        elif key == ord("q") or key == ord("Q"):  # Allow 'q' to quit
            break
    # End of while True loop (application exit)


def display_str_truncated(text, padding_left):
    """Truncates string to fit window width"""
    max_len = curses.COLS - padding_left - 1  # -1 for safety
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


if __name__ == "__main__":
    # Ensure DB_FILE path is correctly handled if it's relative
    # For simplicity, assuming it's in the current working directory or init_db handles it.
    if not os.path.exists(DB_FILE):
        # This print might be overwritten by curses quickly, but good for pre-curses info
        print(f"Database file '{DB_FILE}' not found. It will be created.")

    init_db()  # Initialize database schema if needed

    try:
        curses.wrapper(run_app)
    except curses.error as e:
        # This message will be visible if curses fails to initialize or during run_app if not caught inside
        print(f"A curses error occurred: {e}")
        print("Tips: Ensure your terminal is capable (e.g., not a dummy terminal).")
        print("Try resizing your terminal window if it is too small.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # curses.wrapper should handle restoring terminal state.
        # This print is for after the application has finished or crashed.
        print("Application terminated.")
