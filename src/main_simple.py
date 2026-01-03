#!/usr/bin/env python3
"""
kLibby - Simple text-based interface (no curses)
For Kindles where curses doesn't work well
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from libby.client import LibbyClient
from libby.models import Loan, Hold, Card


class KLibbySimple:
    """Simple text-based kLibby interface"""

    def __init__(self):
        """Initialize application"""
        self.client = LibbyClient()
        self.running = True

    def clear_screen(self):
        """Clear the screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self, title: str):
        """Print header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60 + "\n")

    def print_menu(self, title: str, options: list[str]):
        """Print menu and get selection"""
        self.clear_screen()
        self.print_header(title)

        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        print("\n" + "-" * 60)
        choice = input("\nEnter choice (or 'q' to quit): ").strip()

        if choice.lower() == 'q':
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass

        return -1  # Invalid choice

    def show_message(self, title: str, message: str, wait: bool = True):
        """Show a message"""
        self.clear_screen()
        self.print_header(title)
        print(message)
        if wait:
            input("\nPress Enter to continue...")

    def get_input(self, prompt: str) -> str:
        """Get user input"""
        return input(f"\n{prompt}: ").strip()

    def setup_auth(self):
        """Setup authentication"""
        if self.client.is_authenticated():
            self.show_message(
                "Already Authenticated",
                "You are already logged in to Libby.\n\n"
                "To logout, go to Settings > Clear Authentication."
            )
            return

        self.show_message(
            "Libby Authentication",
            "NEW Authentication Flow (2024+):\n\n"
            "1. kLibby will generate an 8-digit code\n"
            "2. You enter this code in your Libby app\n"
            "3. On phone/tablet: Libby → Settings (⋮)\n"
            "4. Select 'Copy To Another Device'\n"
            "5. Enter the code shown next",
            wait=True
        )

        try:
            # Generate setup code
            self.show_message("Generating...", "Generating setup code...", wait=False)

            response = self.client.generate_clone_code()
            code = response.get('code', '')

            if not code:
                self.show_message("Error", "Failed to generate code. Please try again.")
                return

            # Display the code
            self.clear_screen()
            self.print_header("Your Setup Code")
            print("\n")
            print("  " + "=" * 40)
            print(f"      {code[:4]} - {code[4:]}")
            print("  " + "=" * 40)
            print("\n")
            print("  Enter this code in your Libby app:")
            print("  1. Open Libby on phone/tablet")
            print("  2. Go to Settings (⋮)")
            print("  3. Select 'Copy To Another Device'")
            print(f"  4. Enter: {code}")
            print("\n")
            print("  Polling will start in 3 seconds...")
            print("  Enter the code whenever you're ready.")
            print("\n")

            import time
            time.sleep(3)  # Brief pause to read the code

            # Poll for authentication - starts automatically
            import time
            max_attempts = 90  # 90 attempts × 2 seconds = 3 minutes

            for attempt in range(max_attempts):
                # Show progress
                elapsed = attempt * 2
                self.show_message(
                    "Waiting for Sync...",
                    f"Checking authentication...\n\n"
                    f"Elapsed: {elapsed}s / {max_attempts * 2}s\n"
                    f"Attempt: {attempt + 1} / {max_attempts}\n\n"
                    f"The Libby app should show 'Syncing data'.\n"
                    f"This can take 1-3 minutes depending on your library size.",
                    wait=False
                )

                try:
                    # Check if authentication completed
                    sync_data = self.client.verify_clone_status()

                    if sync_data.get('cards'):
                        # Successfully authenticated!
                        self.show_message(
                            "Success!",
                            "Successfully connected to your Libby account!\n\n"
                            "You can now browse and checkout books."
                        )
                        return

                except Exception as e:
                    # Not authenticated yet, keep waiting
                    # But log unexpected errors for debugging
                    error_msg = str(e).lower()
                    if 'cards' not in error_msg and 'sync' not in error_msg:
                        # Unexpected error, might want to see it
                        pass

                time.sleep(2)  # Wait 2 seconds between checks

            # Timeout
            self.show_message(
                "Timeout",
                "Authentication timed out.\n\n"
                "The code may have expired.\n"
                "Please try again."
            )

        except Exception as e:
            self.show_message("Error", f"Authentication failed:\n{str(e)}")

    def view_loans(self):
        """View active loans"""
        if not self.client.is_authenticated():
            self.show_message("Not Authenticated", "Please authenticate with Libby first.")
            return

        try:
            loans = self.client.get_loans()

            if not loans:
                self.show_message("No Loans", "You don't have any active loans.")
                return

            # Show loans
            while True:
                options = []
                for loan in loans:
                    title = loan.title.title if loan.title else "Unknown"
                    authors = ", ".join(loan.title.authors) if loan.title and loan.title.authors else ""
                    expire = loan.expire_date.strftime("%Y-%m-%d") if loan.expire_date else "Unknown"

                    label = f"{title}"
                    if authors:
                        label += f" by {authors}"
                    label += f" (expires: {expire})"

                    options.append(label)

                options.append("← Back")

                choice = self.print_menu("Your Loans", options)

                if choice is None or choice == len(options) - 1:
                    break
                elif choice == -1:
                    self.show_message("Error", "Invalid choice")
                    continue
                else:
                    self.loan_actions(loans[choice])

        except Exception as e:
            self.show_message("Error", f"Failed to load loans:\n{str(e)}")

    def loan_actions(self, loan: Loan):
        """Show actions for a loan"""
        title = loan.title.title if loan.title else "Unknown"

        while True:
            options = [
                "Download Book",
                "Return Early",
                "← Back"
            ]

            choice = self.print_menu(f"Loan: {title}", options)

            if choice is None or choice == 2:
                break
            elif choice == 0:
                self.download_loan(loan)
            elif choice == 1:
                self.return_loan(loan)

    def download_loan(self, loan: Loan):
        """Download a book"""
        try:
            self.show_message("Downloading...", "Downloading book...", wait=False)

            # Create downloads directory
            downloads_dir = Path.home() / "kLibby" / "downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)

            # Sanitize filename
            filename = loan.title.title.replace('/', '-').replace('\\', '-')
            output_path = downloads_dir / f"{filename}.epub"

            # Try open format first
            try:
                self.client.download_book(
                    loan.card_id,
                    loan.loan_id,
                    str(output_path),
                    format_type='ebook-epub-open'
                )
            except:
                # Fallback to Adobe DRM
                output_path = downloads_dir / f"{filename}.acsm"
                self.client.download_book(
                    loan.card_id,
                    loan.loan_id,
                    str(output_path),
                    format_type='ebook-epub-adobe'
                )

            self.show_message(
                "Download Complete",
                f"Book downloaded to:\n{output_path}\n\n"
                f"You can now read it with an ePub reader."
            )

        except Exception as e:
            self.show_message("Error", f"Download failed:\n{str(e)}")

    def return_loan(self, loan: Loan):
        """Return a loan"""
        title = loan.title.title if loan.title else "Unknown"

        confirm = self.get_input(f"Return '{title}'? (yes/no)")

        if confirm.lower() in ['yes', 'y']:
            try:
                self.show_message("Returning...", "Returning loan...", wait=False)
                self.client.return_loan(loan.card_id, loan.loan_id)
                self.show_message("Success", f"'{title}' has been returned.")
            except Exception as e:
                self.show_message("Error", f"Return failed:\n{str(e)}")

    def view_holds(self):
        """View holds"""
        if not self.client.is_authenticated():
            self.show_message("Not Authenticated", "Please authenticate with Libby first.")
            return

        try:
            holds = self.client.get_holds()

            if not holds:
                self.show_message("No Holds", "You don't have any holds.")
                return

            # Display holds
            holds_text = ""
            for hold in holds:
                title = hold.title.title if hold.title else "Unknown"
                status = "Available!" if hold.available else "Waiting"
                holds_text += f"• {title} ({status})\n"

            self.show_message("Your Holds", holds_text)

        except Exception as e:
            self.show_message("Error", f"Failed to load holds:\n{str(e)}")

    def view_cards(self):
        """View library cards"""
        if not self.client.is_authenticated():
            self.show_message("Not Authenticated", "Please authenticate with Libby first.")
            return

        try:
            cards = self.client.get_cards()

            if not cards:
                self.show_message("No Cards", "You don't have any library cards.")
                return

            # Display cards
            cards_text = ""
            for card in cards:
                cards_text += f"• {card.library_name}\n"
                if card.username:
                    cards_text += f"  User: {card.username}\n"

            self.show_message("Your Library Cards", cards_text)

        except Exception as e:
            self.show_message("Error", f"Failed to load cards:\n{str(e)}")

    def clear_auth(self):
        """Clear authentication"""
        confirm = self.get_input("Logout from Libby? (yes/no)")

        if confirm.lower() in ['yes', 'y']:
            self.client.clear_auth()
            self.show_message("Logged Out", "You have been logged out of Libby.")

    def about(self):
        """Show about"""
        self.show_message(
            "About kLibby",
            "kLibby v0.1.0\n\n"
            "A Libby client for jailbroken Kindle devices.\n\n"
            "Not affiliated with OverDrive, Inc.\n"
            "For personal use with valid library credentials only.\n\n"
            "https://github.com/cyberchicken1231/kLibby"
        )

    def main_menu(self):
        """Main menu"""
        while self.running:
            if not self.client.is_authenticated():
                options = [
                    "Connect to Libby",
                    "About",
                    "Quit"
                ]

                choice = self.print_menu("kLibby - Libby for Kindle", options)

                if choice is None or choice == 2:
                    self.running = False
                elif choice == 0:
                    self.setup_auth()
                elif choice == 1:
                    self.about()
                elif choice == -1:
                    self.show_message("Error", "Invalid choice")

            else:
                options = [
                    "My Loans",
                    "My Holds",
                    "Library Cards",
                    "Settings",
                    "About",
                    "Quit"
                ]

                choice = self.print_menu("kLibby - Libby for Kindle", options)

                if choice is None or choice == 5:
                    self.running = False
                elif choice == 0:
                    self.view_loans()
                elif choice == 1:
                    self.view_holds()
                elif choice == 2:
                    self.view_cards()
                elif choice == 3:
                    self.settings_menu()
                elif choice == 4:
                    self.about()
                elif choice == -1:
                    self.show_message("Error", "Invalid choice")

    def settings_menu(self):
        """Settings menu"""
        while True:
            options = [
                "Clear Authentication",
                "← Back"
            ]

            choice = self.print_menu("Settings", options)

            if choice is None or choice == 1:
                break
            elif choice == 0:
                self.clear_auth()
            elif choice == -1:
                self.show_message("Error", "Invalid choice")

    def run(self):
        """Run the application"""
        try:
            self.main_menu()
            self.clear_screen()
            print("\nThank you for using kLibby!\n")
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n\nGoodbye!\n")
        except Exception as e:
            print(f"\nFatal error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    app = KLibbySimple()
    app.run()


if __name__ == "__main__":
    main()
