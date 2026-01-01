"""
Simple menu-based UI optimized for e-ink displays
Uses curses for terminal-based interface
"""

from __future__ import annotations

import curses
from typing import Callable, Any
from enum import Enum


class MenuAction(Enum):
    """Menu action types"""
    CONTINUE = 1
    BACK = 2
    QUIT = 3


class MenuItem:
    """Represents a menu item"""

    def __init__(self, label: str, action: Callable[[], Any], description: str = ""):
        """
        Create a menu item

        Args:
            label: Display text for the menu item
            action: Function to call when selected
            description: Optional description shown below menu
        """
        self.label = label
        self.action = action
        self.description = description


class MenuUI:
    """Simple menu-based UI for e-ink displays"""

    def __init__(self, stdscr=None):
        """
        Initialize UI

        Args:
            stdscr: Curses screen object (optional, created if not provided)
        """
        self.stdscr = stdscr
        self.running = False

    def init_curses(self):
        """Initialize curses"""
        if not self.stdscr:
            self.stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(0)  # Hide cursor

        # Try to use colors if available (high contrast for e-ink)
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlighted
        except:
            pass

    def cleanup_curses(self):
        """Cleanup curses"""
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()

    def draw_header(self, title: str, row: int = 0) -> int:
        """
        Draw header section

        Args:
            title: Header title
            row: Starting row

        Returns:
            Next available row
        """
        height, width = self.stdscr.getmaxyx()

        # Title
        self.stdscr.addstr(row, 0, "=" * width)
        row += 1

        # Center the title
        title_x = max(0, (width - len(title)) // 2)
        self.stdscr.addstr(row, title_x, title, curses.A_BOLD)
        row += 1

        self.stdscr.addstr(row, 0, "=" * width)
        row += 2

        return row

    def draw_menu(
        self,
        title: str,
        items: list[MenuItem],
        selected_idx: int = 0,
        info_text: str = ""
    ) -> None:
        """
        Draw menu

        Args:
            title: Menu title
            items: List of menu items
            selected_idx: Currently selected item index
            info_text: Optional info text to display at bottom
        """
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Draw header
        row = self.draw_header(title)

        # Draw menu items
        for idx, item in enumerate(items):
            if row >= height - 3:  # Leave room for footer
                break

            # Highlight selected item
            if idx == selected_idx:
                try:
                    self.stdscr.addstr(row, 2, f"> {item.label}", curses.color_pair(1) | curses.A_BOLD)
                except:
                    self.stdscr.addstr(row, 2, f"> {item.label}", curses.A_REVERSE)
            else:
                self.stdscr.addstr(row, 4, item.label)

            row += 1

        # Draw footer with instructions
        footer_row = height - 2
        self.stdscr.addstr(footer_row, 0, "-" * width)
        footer_row += 1

        controls = "↑/↓: Navigate | Enter: Select | Q: Quit"
        self.stdscr.addstr(footer_row, 2, controls[:width-4])

        # Draw info text if provided
        if info_text and row < height - 4:
            self.stdscr.addstr(row + 1, 2, info_text[:width-4])

        self.stdscr.refresh()

    def show_menu(self, title: str, items: list[MenuItem]) -> MenuAction:
        """
        Display menu and handle navigation

        Args:
            title: Menu title
            items: List of menu items

        Returns:
            MenuAction indicating what to do next
        """
        if not items:
            return MenuAction.BACK

        selected_idx = 0

        while True:
            # Draw the menu
            info_text = items[selected_idx].description if items[selected_idx].description else ""
            self.draw_menu(title, items, selected_idx, info_text)

            # Get input
            key = self.stdscr.getch()

            # Navigation
            if key == curses.KEY_UP or key == ord('k'):
                selected_idx = (selected_idx - 1) % len(items)
            elif key == curses.KEY_DOWN or key == ord('j'):
                selected_idx = (selected_idx + 1) % len(items)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Execute selected action
                result = items[selected_idx].action()
                if result == MenuAction.BACK:
                    return MenuAction.BACK
                elif result == MenuAction.QUIT:
                    return MenuAction.QUIT
            elif key == ord('q') or key == ord('Q'):
                return MenuAction.QUIT
            elif key == ord('b') or key == ord('B'):
                return MenuAction.BACK

    def show_message(
        self,
        title: str,
        message: str,
        wait_for_key: bool = True
    ) -> None:
        """
        Display a message screen

        Args:
            title: Message title
            message: Message text (can be multiline)
            wait_for_key: Wait for key press before returning
        """
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Draw header
        row = self.draw_header(title)

        # Draw message (word wrap)
        lines = message.split('\n')
        for line in lines:
            if row >= height - 3:
                break

            # Simple word wrap
            while len(line) > width - 4:
                # Find last space before width
                wrap_pos = line.rfind(' ', 0, width - 4)
                if wrap_pos == -1:
                    wrap_pos = width - 4

                self.stdscr.addstr(row, 2, line[:wrap_pos])
                line = line[wrap_pos:].lstrip()
                row += 1

            if line:
                self.stdscr.addstr(row, 2, line)
                row += 1

        # Footer
        if wait_for_key:
            footer_row = height - 2
            self.stdscr.addstr(footer_row, 0, "-" * width)
            footer_row += 1
            self.stdscr.addstr(footer_row, 2, "Press any key to continue...")

        self.stdscr.refresh()

        if wait_for_key:
            self.stdscr.getch()

    def get_input(
        self,
        title: str,
        prompt: str,
        default: str = ""
    ) -> str | None:
        """
        Get text input from user

        Args:
            title: Input screen title
            prompt: Prompt text
            default: Default value

        Returns:
            User input string or None if cancelled
        """
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Draw header
        row = self.draw_header(title)

        # Draw prompt
        self.stdscr.addstr(row, 2, prompt)
        row += 2

        # Enable echo and cursor for input
        curses.echo()
        curses.curs_set(1)

        # Get input
        input_row = row
        input_col = 2

        if default:
            self.stdscr.addstr(input_row, input_col, default)

        self.stdscr.move(input_row, input_col)
        self.stdscr.refresh()

        try:
            user_input = self.stdscr.getstr(input_row, input_col, width - 4).decode('utf-8')
        except:
            user_input = None
        finally:
            # Disable echo and cursor
            curses.noecho()
            curses.curs_set(0)

        return user_input if user_input else default

    def show_list(
        self,
        title: str,
        items: list[str],
        selected_callback: Callable[[int], Any] | None = None
    ) -> MenuAction:
        """
        Display a selectable list

        Args:
            title: List title
            items: List of strings to display
            selected_callback: Function to call when item is selected

        Returns:
            MenuAction
        """
        # Convert strings to menu items
        menu_items = []
        for idx, item in enumerate(items):
            action = lambda i=idx: selected_callback(i) if selected_callback else MenuAction.BACK
            menu_items.append(MenuItem(item, action))

        return self.show_menu(title, menu_items)

    def run(self, main_menu_fn: Callable[[], list[MenuItem]]) -> None:
        """
        Run the UI main loop

        Args:
            main_menu_fn: Function that returns the main menu items
        """
        try:
            self.init_curses()
            self.running = True

            while self.running:
                items = main_menu_fn()
                result = self.show_menu("kLibby - Libby for Kindle", items)

                if result == MenuAction.QUIT:
                    break

        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup_curses()
