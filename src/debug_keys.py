#!/usr/bin/env python3
"""
Debug script to see what key codes Kindle sends
"""
import curses
import sys

def main(stdscr):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

    stdscr.clear()
    stdscr.addstr(0, 0, "Key Code Debugger - Press keys to see their codes")
    stdscr.addstr(1, 0, "Press 'q' to quit")
    stdscr.addstr(2, 0, "=" * 60)

    row = 4

    while True:
        stdscr.addstr(3, 0, "Waiting for key press...                    ")
        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break

        # Display key info
        msg = f"Key pressed: {key} (decimal) = 0x{key:02x} (hex)"
        if 32 <= key <= 126:
            msg += f" = '{chr(key)}' (char)"

        # Check against known codes
        known = []
        if key == curses.KEY_UP:
            known.append("curses.KEY_UP")
        if key == curses.KEY_DOWN:
            known.append("curses.KEY_DOWN")
        if key == curses.KEY_ENTER:
            known.append("curses.KEY_ENTER")
        if key == 10:
            known.append("newline (10)")
        if key == 13:
            known.append("carriage return (13)")
        if key == 259:
            known.append("alternate UP (259)")
        if key == 258:
            known.append("alternate DOWN (258)")

        if known:
            msg += f" -> {', '.join(known)}"

        stdscr.addstr(row, 0, msg + " " * 20)
        row += 1

        if row > 20:
            row = 4
            stdscr.clear()
            stdscr.addstr(0, 0, "Key Code Debugger - Press keys to see their codes")
            stdscr.addstr(1, 0, "Press 'q' to quit")
            stdscr.addstr(2, 0, "=" * 60)

    stdscr.addstr(22, 0, "Exiting...")
    stdscr.refresh()
    curses.napms(500)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
