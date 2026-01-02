#!/usr/bin/env python3
"""
kLibby - Libby client for jailbroken Kindle
Main application entry point
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from libby.client import LibbyClient
from libby.models import Loan, Hold, Card
from ui.menu import MenuUI, MenuItem, MenuAction


class KLibbyApp:
    """Main kLibby application"""

    def __init__(self):
        """Initialize application"""
        self.client = LibbyClient()
        self.ui = MenuUI()
        self.current_cards: list[Card] = []
        self.current_loans: list[Loan] = []
        self.current_holds: list[Hold] = []

    def setup_auth(self) -> MenuAction:
        """Setup Libby authentication (NEW 2024+ flow)"""
        if self.client.is_authenticated():
            self.ui.show_message(
                "Already Authenticated",
                "You are already logged in to Libby.\n\n"
                "To logout, go to Settings > Clear Authentication."
            )
            return MenuAction.BACK

        self.ui.show_message(
            "Libby Authentication",
            "NEW Authentication Flow (2024+):\n\n"
            "1. kLibby will generate an 8-digit code\n"
            "2. You enter this code in your Libby app\n"
            "3. On phone/tablet: Libby → Settings (⋮)\n"
            "4. Select 'Copy To Another Device'\n"
            "5. Enter the code shown next\n\n"
            "Press Enter to generate code..."
        )

        try:
            # Generate setup code
            self.ui.show_message("Generating...", "Generating setup code...", wait_for_key=False)

            response = self.client.generate_clone_code()
            code = response.get('code', '')

            if not code:
                self.ui.show_message("Error", "Failed to generate code. Please try again.")
                return MenuAction.BACK

            # Display the code to user
            self.ui.show_message(
                "Your Setup Code",
                f"═══════════════════════════════\n"
                f"    {code[:4]} - {code[4:]}\n"
                f"═══════════════════════════════\n\n"
                f"Enter this code in your Libby app:\n"
                f"1. Open Libby on phone/tablet\n"
                f"2. Go to Settings (⋮)\n"
                f"3. Select 'Copy To Another Device'\n"
                f"4. Enter: {code}\n\n"
                f"Press Enter after entering the code..."
            )

            # Poll for authentication
            self.ui.show_message("Waiting...", "Checking authentication...", wait_for_key=False)

            import time
            max_attempts = 30  # 30 attempts = ~1 minute
            for attempt in range(max_attempts):
                try:
                    # Check if authentication completed
                    sync_data = self.client.verify_clone_status()

                    if sync_data.get('cards'):
                        # Successfully authenticated!
                        self.ui.show_message(
                            "Success!",
                            "Successfully connected to your Libby account!\n\n"
                            "You can now browse and checkout books."
                        )

                        # Load initial data
                        self._refresh_data()
                        return MenuAction.BACK

                except Exception:
                    # Not authenticated yet, keep waiting
                    pass

                time.sleep(2)  # Wait 2 seconds between checks

            # Timeout
            self.ui.show_message(
                "Timeout",
                "Authentication timed out.\n\n"
                "The code may have expired.\n"
                "Please try again."
            )

        except Exception as e:
            self.ui.show_message("Error", f"Authentication failed:\n{str(e)}")

        return MenuAction.BACK

    def _refresh_data(self) -> None:
        """Refresh library data from Libby"""
        try:
            self.current_cards = self.client.get_cards()
            self.current_loans = self.client.get_loans()
            self.current_holds = self.client.get_holds()
        except Exception as e:
            self.ui.show_message("Error", f"Failed to refresh data:\n{str(e)}")

    def view_loans(self) -> MenuAction:
        """View active loans"""
        if not self.client.is_authenticated():
            self.ui.show_message("Not Authenticated", "Please authenticate with Libby first.")
            return MenuAction.BACK

        self.ui.show_message("Loading...", "Loading your loans...", wait_for_key=False)

        try:
            self.current_loans = self.client.get_loans()

            if not self.current_loans:
                self.ui.show_message("No Loans", "You don't have any active loans.")
                return MenuAction.BACK

            # Create menu items for each loan
            menu_items = []
            for loan in self.current_loans:
                title = loan.title.title if loan.title else "Unknown"
                authors = ", ".join(loan.title.authors) if loan.title and loan.title.authors else ""
                label = f"{title}"
                if authors:
                    label += f" - {authors}"

                expire_str = loan.expire_date.strftime("%Y-%m-%d") if loan.expire_date else "Unknown"

                menu_items.append(MenuItem(
                    label,
                    lambda l=loan: self.loan_actions(l),
                    f"Expires: {expire_str}"
                ))

            menu_items.append(MenuItem("← Back", lambda: MenuAction.BACK))

            return self.ui.show_menu("Your Loans", menu_items)

        except Exception as e:
            self.ui.show_message("Error", f"Failed to load loans:\n{str(e)}")
            return MenuAction.BACK

    def loan_actions(self, loan: Loan) -> MenuAction:
        """Show actions for a specific loan"""
        title = loan.title.title if loan.title else "Unknown"

        menu_items = [
            MenuItem(
                "Download Book",
                lambda: self.download_loan(loan),
                "Download this book to read"
            ),
            MenuItem(
                "Return Early",
                lambda: self.return_loan(loan),
                "Return this loan before it expires"
            ),
            MenuItem("← Back", lambda: MenuAction.BACK)
        ]

        return self.ui.show_menu(f"Loan: {title}", menu_items)

    def download_loan(self, loan: Loan) -> MenuAction:
        """Download a loaned book"""
        try:
            self.ui.show_message("Downloading...", "Downloading book...", wait_for_key=False)

            # Create downloads directory
            downloads_dir = Path.home() / "kLibby" / "downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)

            # Sanitize filename
            filename = loan.title.title.replace('/', '-').replace('\\', '-')
            output_path = downloads_dir / f"{filename}.epub"

            # Try open format first, fallback to Adobe DRM
            try:
                self.client.download_book(
                    loan.card_id,
                    loan.loan_id,
                    str(output_path),
                    format_type='ebook-epub-open'
                )
            except:
                # Fallback to Adobe DRM format
                output_path = downloads_dir / f"{filename}.acsm"
                self.client.download_book(
                    loan.card_id,
                    loan.loan_id,
                    str(output_path),
                    format_type='ebook-epub-adobe'
                )

            self.ui.show_message(
                "Download Complete",
                f"Book downloaded to:\n{output_path}\n\n"
                f"You can now read it with an ePub reader."
            )

        except Exception as e:
            self.ui.show_message("Error", f"Download failed:\n{str(e)}")

        return MenuAction.BACK

    def return_loan(self, loan: Loan) -> MenuAction:
        """Return a loan early"""
        title = loan.title.title if loan.title else "Unknown"

        # Confirm
        self.ui.show_message(
            "Confirm Return",
            f"Are you sure you want to return:\n{title}\n\n"
            f"Press Enter to confirm, or B to cancel."
        )

        try:
            self.ui.show_message("Returning...", "Returning loan...", wait_for_key=False)

            self.client.return_loan(loan.card_id, loan.loan_id)

            self.ui.show_message("Success", f"'{title}' has been returned.")

            # Refresh loans
            self._refresh_data()

        except Exception as e:
            self.ui.show_message("Error", f"Return failed:\n{str(e)}")

        return MenuAction.BACK

    def view_holds(self) -> MenuAction:
        """View holds"""
        if not self.client.is_authenticated():
            self.ui.show_message("Not Authenticated", "Please authenticate with Libby first.")
            return MenuAction.BACK

        self.ui.show_message("Loading...", "Loading your holds...", wait_for_key=False)

        try:
            self.current_holds = self.client.get_holds()

            if not self.current_holds:
                self.ui.show_message("No Holds", "You don't have any holds.")
                return MenuAction.BACK

            # Display holds
            holds_text = ""
            for hold in self.current_holds:
                title = hold.title.title if hold.title else "Unknown"
                status = "Available!" if hold.available else "Waiting"
                holds_text += f"• {title} ({status})\n"

            self.ui.show_message("Your Holds", holds_text)

        except Exception as e:
            self.ui.show_message("Error", f"Failed to load holds:\n{str(e)}")

        return MenuAction.BACK

    def view_cards(self) -> MenuAction:
        """View library cards"""
        if not self.client.is_authenticated():
            self.ui.show_message("Not Authenticated", "Please authenticate with Libby first.")
            return MenuAction.BACK

        try:
            self.current_cards = self.client.get_cards()

            if not self.current_cards:
                self.ui.show_message("No Cards", "You don't have any library cards.")
                return MenuAction.BACK

            # Display cards
            cards_text = ""
            for card in self.current_cards:
                cards_text += f"• {card.library_name}\n"
                if card.username:
                    cards_text += f"  User: {card.username}\n"

            self.ui.show_message("Your Library Cards", cards_text)

        except Exception as e:
            self.ui.show_message("Error", f"Failed to load cards:\n{str(e)}")

        return MenuAction.BACK

    def clear_auth(self) -> MenuAction:
        """Clear authentication"""
        self.client.clear_auth()
        self.current_cards = []
        self.current_loans = []
        self.current_holds = []

        self.ui.show_message("Logged Out", "You have been logged out of Libby.")
        return MenuAction.BACK

    def about(self) -> MenuAction:
        """Show about screen"""
        self.ui.show_message(
            "About kLibby",
            "kLibby v0.1.0\n\n"
            "A Libby client for jailbroken Kindle devices.\n\n"
            "Not affiliated with OverDrive, Inc.\n"
            "For personal use with valid library credentials only.\n\n"
            "https://github.com/cyberchicken1231/kLibby"
        )
        return MenuAction.BACK

    def get_main_menu(self) -> list[MenuItem]:
        """Get main menu items"""
        if not self.client.is_authenticated():
            return [
                MenuItem(
                    "Connect to Libby",
                    self.setup_auth,
                    "Link kLibby to your Libby account"
                ),
                MenuItem(
                    "About",
                    self.about,
                    "About kLibby"
                ),
                MenuItem(
                    "Quit",
                    lambda: MenuAction.QUIT,
                    "Exit kLibby"
                )
            ]
        else:
            return [
                MenuItem(
                    "My Loans",
                    self.view_loans,
                    "View and manage your checked out books"
                ),
                MenuItem(
                    "My Holds",
                    self.view_holds,
                    "View your holds and waiting list"
                ),
                MenuItem(
                    "Library Cards",
                    self.view_cards,
                    "View your library cards"
                ),
                MenuItem(
                    "Settings",
                    self.settings_menu,
                    "Application settings"
                ),
                MenuItem(
                    "About",
                    self.about,
                    "About kLibby"
                ),
                MenuItem(
                    "Quit",
                    lambda: MenuAction.QUIT,
                    "Exit kLibby"
                )
            ]

    def settings_menu(self) -> MenuAction:
        """Settings menu"""
        menu_items = [
            MenuItem(
                "Clear Authentication",
                self.clear_auth,
                "Logout from Libby"
            ),
            MenuItem("← Back", lambda: MenuAction.BACK)
        ]

        return self.ui.show_menu("Settings", menu_items)

    def run(self) -> None:
        """Run the application"""
        try:
            self.ui.run(self.get_main_menu)
        except Exception as e:
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    app = KLibbyApp()
    app.run()


if __name__ == "__main__":
    main()
