import curses
import subprocess
import sys
import textwrap

def run_git_commands(message):
    """Execute git commands: add, commit, push"""
    try:
        # Git add
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

        # Git commit
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)

        # Git push
        subprocess.run(["git", "push"], check=True, capture_output=True)

        return True, "Successfully pushed changes!"
    except subprocess.CalledProcessError as e:
        return False, f"Git command failed: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def draw_box(window, y, x, h, w, title=""):
    """Draw a box with optional title"""
    window.attron(curses.color_pair(1))

    # Draw corners
    window.addch(y, x, curses.ACS_ULCORNER)
    window.addch(y, x + w - 1, curses.ACS_URCORNER)
    window.addch(y + h - 1, x, curses.ACS_LLCORNER)
    window.addch(y + h - 1, x + w - 1, curses.ACS_LRCORNER)

    # Draw horizontal lines
    for i in range(1, w - 1):
        window.addch(y, x + i, curses.ACS_HLINE)
        window.addch(y + h - 1, x + i, curses.ACS_HLINE)

    # Draw vertical lines
    for i in range(1, h - 1):
        window.addch(y + i, x, curses.ACS_VLINE)
        window.addch(y + i, x + w - 1, curses.ACS_VLINE)

    # Add title if provided
    if title:
        window.addstr(y, x + 2, f" {title} ", curses.color_pair(2) | curses.A_BOLD)

    window.attroff(curses.color_pair(1))

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Set up colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Hide cursor initially
    curses.curs_set(1)

    # Get terminal size
    height, width = stdscr.getmaxyx()

    # Calculate box dimensions
    box_width = min(70, width - 4)
    box_height = 10
    box_y = (height - box_height - 6) // 2
    box_x = (width - box_width) // 2

    # Input area inside the box
    input_y = box_y + 3
    input_x = box_x + 3
    input_width = box_width - 6
    input_height = 4

    message = ""
    status_message = ""
    status_color = 2

    while True:
        stdscr.clear()

        # Draw title
        title = "gpush Terminal Interface"
        title_y = box_y - 2
        title_x = (width - len(title)) // 2
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(title_y, title_x, title)
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        # Draw the main box
        draw_box(stdscr, box_y, box_x, box_height, box_width, "Commit Message")

        # Draw instructions
        instructions = ["Enter your commit message below:",
                       "Press ENTER to commit and push",
                       "Press ESC to cancel"]
        for i, instruction in enumerate(instructions):
            stdscr.addstr(box_y + 1 + i, box_x + 3, instruction, curses.color_pair(5))

        # Draw input area background
        for i in range(input_height):
            stdscr.addstr(input_y + i, input_x, "." * input_width, curses.color_pair(1) | curses.A_DIM)

        # Display the message with word wrapping
        if message:
            wrapped_lines = textwrap.wrap(message, width=input_width)
            for i, line in enumerate(wrapped_lines[:input_height]):
                stdscr.addstr(input_y + i, input_x, line, curses.color_pair(2))

        # Show cursor position
        cursor_pos = len(message) % input_width
        cursor_line = len(message) // input_width
        if cursor_line < input_height:
            stdscr.move(input_y + cursor_line, input_x + cursor_pos)

        # Display status message if any
        if status_message:
            status_y = box_y + box_height + 1
            status_x = (width - len(status_message)) // 2
            stdscr.attron(curses.color_pair(status_color))
            stdscr.addstr(status_y, status_x, status_message)
            stdscr.attroff(curses.color_pair(status_color))

        # Display character count
        char_count = f"Characters: {len(message)}"
        stdscr.addstr(box_y + box_height - 2, box_x + box_width - len(char_count) - 4,
                     char_count, curses.color_pair(1))

        stdscr.refresh()

        # Get user input
        key = stdscr.getch()

        if key == 27:  # ESC key
            break
        elif key == ord('\n'):  # Enter key
            if message.strip():
                # Show processing message
                stdscr.addstr(box_y + box_height + 1,
                            (width - len("Processing...")) // 2,
                            "Processing...",
                            curses.color_pair(5) | curses.A_BLINK)
                stdscr.refresh()

                # Run git commands
                success, result = run_git_commands(message.strip())

                if success:
                    status_message = result
                    status_color = 3  # Green
                    message = ""  # Clear message on success
                else:
                    status_message = result
                    status_color = 4  # Red
            else:
                status_message = "Please enter a commit message!"
                status_color = 4
        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
            if message:
                message = message[:-1]
                status_message = ""
        elif 32 <= key <= 126:  # Printable characters
            if len(message) < input_width * input_height:
                message += chr(key)
                status_message = ""

if __name__ == "__main__":
    curses.wrapper(main)
