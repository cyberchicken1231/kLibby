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

        # Choose authentication method
        options = [
            "Use Browser Token (For Downloads - Recommended)",
            "I'll get a code FROM Libby",
            "Generate code for Libby to scan",
            "← Back"
        ]

        choice = self.print_menu("Libby Authentication", options)

        if choice is None or choice == 3:
            return
        elif choice == 0:
            self.setup_auth_browser_token()
        elif choice == 1:
            self.setup_auth_old_flow()
        elif choice == 2:
            self.setup_auth_new_flow()

    def setup_auth_old_flow(self):
        """OLD flow: Libby gives you the code"""
        self.show_message(
            "Get Code from Libby",
            "1. Open Libby on phone/tablet\n"
            "2. Go to Settings (⋮) → Copy To Another Device\n"
            "3. Select 'Sonos' or 'Android Automotive'\n"
            "4. Libby will show you an 8-digit code\n"
            "5. Enter that code in the next screen",
            wait=True
        )

        code = self.get_input("Enter the 8-digit code from Libby")

        if not code or len(code) != 8 or not code.isdigit():
            self.show_message("Error", "Invalid code. Must be 8 digits.")
            return

        try:
            self.show_message("Connecting...", "Authenticating with Libby...", wait=False)

            # Use the code to authenticate
            response = self.client.clone_by_code(code)

            # Verify authentication
            sync_data = self.client.sync()

            if sync_data.get('cards'):
                self.show_message(
                    "Success!",
                    "Successfully connected to your Libby account!\n\n"
                    "You can now browse and checkout books."
                )
            else:
                self.show_message(
                    "Error",
                    "Authentication completed but no library cards found.\n\n"
                    "Make sure you have at least one library card\n"
                    "added in your Libby app."
                )

        except Exception as e:
            self.show_message("Error", f"Authentication failed:\n{str(e)}")

    def setup_auth_new_flow(self):
        """NEW flow: kLibby generates code for user to enter in Libby"""
        self.show_message(
            "Libby Authentication",
            "NEW Authentication Flow:\n\n"
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
                    # CRITICAL: After user enters code in Libby, we need to
                    # "claim" the authentication by calling clone_by_code with
                    # the SAME code we generated. This returns authenticated token.
                    if attempt == 5:  # After 10 seconds, try to claim
                        try:
                            print(f"\nDEBUG: Attempting to claim with code {code}...")
                            claim_response = self.client.clone_by_code(code)
                            print(f"DEBUG: Claim response: {claim_response}")
                            # If it returns a new identity, we're authenticated
                            if claim_response.get('identity'):
                                print(f"DEBUG: Got new identity token!")
                        except Exception as claim_error:
                            print(f"DEBUG: Claim failed: {claim_error}")

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

    def setup_auth_browser_token(self):
        """Browser token flow: Extract token from libbyapp.com"""
        self.show_message(
            "Browser Token Authentication",
            "This method gives FULL download permissions!\n\n"
            "HOW TO GET YOUR TOKEN:\n"
            "1. Go to https://libbyapp.com in a web browser\n"
            "2. Sign in with your library card\n"
            "3. Press F12 to open DevTools\n"
            "4. Click the 'Network' tab\n"
            "5. Click on any book in Libby\n"
            "6. In Network tab, click any request\n"
            "7. Find 'Authorization' in Request Headers\n"
            "8. Copy the FULL token value\n"
            "   (long string starting with 'eyJ...')\n\n"
            "NOTE: You can paste the full header including\n"
            "'Bearer ' prefix, or just the token itself.",
            wait=True
        )

        token = self.get_input(
            "Paste your browser token here:\n"
            "(it will be very long - that's normal)"
        )

        if not token:
            self.show_message("Cancelled", "No token entered.")
            return

        try:
            self.show_message("Verifying...", "Verifying token with Libby...", wait=False)

            # Set and verify the token
            self.client.set_browser_token(token)

            self.show_message(
                "Success!",
                "Browser token authenticated successfully!\n\n"
                "You now have FULL permissions including:\n"
                "- View loans, holds, and cards\n"
                "- Download books in any format\n\n"
                "Your token has been saved and will be\n"
                "used automatically from now on."
            )

        except Exception as e:
            self.show_message(
                "Error",
                f"Token verification failed:\n\n{str(e)}\n\n"
                "Make sure you copied the FULL token value\n"
                "from the Authorization header."
            )

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
        # Check if book is locked to Kindle format
        if loan.is_kindle_locked():
            self.show_message(
                "Cannot Download",
                f"This book was already sent to your Kindle device.\n\n"
                f"Books delivered to Kindle cannot be downloaded in\n"
                f"other formats due to Libby's DRM restrictions.\n\n"
                f"You can read it on your Kindle, or you can:\n"
                f"- Wait for the loan to expire and checkout again\n"
                f"  in a different format\n"
                f"- Read online using OverDrive Read in a browser"
            )
            return

        try:
            self.show_message("Downloading...", "Detecting best format...", wait=False)

            # Auto-detect best format to download
            try:
                format_to_use = loan.get_best_format(prefer_open=True)
            except ValueError as e:
                # Loan is locked to non-downloadable format (e.g., Kindle)
                self.show_message("Cannot Download", str(e))
                return

            if not format_to_use:
                self.show_message(
                    "Cannot Download",
                    "This book has no downloadable formats available.\n\n"
                    "It may only be available for reading online\n"
                    "or on specific devices."
                )
                return

            # Create downloads directory
            downloads_dir = Path.home() / "kLibby" / "downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)

            # Sanitize filename
            filename = loan.title.title.replace('/', '-').replace('\\', '-')

            # Determine file extension based on format
            if 'pdf' in format_to_use:
                file_extension = 'pdf'
            elif 'epub' in format_to_use:
                file_extension = 'epub'
            elif 'mp3' in format_to_use:
                file_extension = 'odm'
            else:
                file_extension = 'epub'  # Default

            # Adobe DRM formats download as .acsm files
            if 'adobe' in format_to_use:
                file_extension = 'acsm'

            output_path = downloads_dir / f"{filename}.{file_extension}"

            # Download the book
            self.show_message("Downloading...", f"Downloading as {format_to_use}...", wait=False)
            self.client.download_book(
                loan.card_id,
                loan.loan_id,
                str(output_path),
                format_type=format_to_use
            )

            # Show appropriate message based on file type
            format_name = format_to_use.upper().replace('-', ' ')
            if file_extension == 'acsm':
                self.show_message(
                    "Download Complete",
                    f"Book downloaded to:\n{output_path}\n\n"
                    f"Format: {format_name}\n\n"
                    f"This is an Adobe DRM file (.acsm).\n"
                    f"You'll need Adobe Digital Editions to open it,\n"
                    f"which will download the actual EPUB/PDF file.\n\n"
                    f"Note: ACSM files may not work on all Kindle devices."
                )
            elif file_extension == 'odm':
                self.show_message(
                    "Download Complete",
                    f"Book downloaded to:\n{output_path}\n\n"
                    f"Format: {format_name}\n\n"
                    f"This is an audiobook manifest file (.odm).\n"
                    f"Use OverDrive Media Console or odmpy to\n"
                    f"download the actual audio files."
                )
            elif 'open' in format_to_use:
                self.show_message(
                    "Download Complete",
                    f"Book downloaded to:\n{output_path}\n\n"
                    f"Format: {format_name} (DRM-free!)\n\n"
                    f"You can read this on any EPUB reader,\n"
                    f"including your Kindle device."
                )
            else:
                self.show_message(
                    "Download Complete",
                    f"Book downloaded to:\n{output_path}\n\n"
                    f"Format: {format_name}\n\n"
                    f"You can now read it with an appropriate reader."
                )

        except Exception as e:
            error_msg = str(e)

            # Show error with helpful debug info
            debug_info = (
                f"Download failed!\n\n"
                f"ERROR: {error_msg}\n\n"
                f"DEBUG INFO:\n"
                f"  Loan ID: {loan.loan_id}\n"
                f"  Card ID: {loan.card_id}\n"
                f"  Format locked: {loan.is_format_locked_in}\n"
                f"  Kindle locked: {loan.is_kindle_locked()}\n"
                f"  Has auth token: {self.client.identity_token is not None}"
            )
            self.show_message("Download Error", debug_info)

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
                error_msg = str(e)
                # Check for Kindle-specific error
                if "CannotEarlyReturnWhenFulfilledOnKindle" in error_msg:
                    self.show_message(
                        "Cannot Return",
                        f"This book was already sent to your Kindle device.\n\n"
                        f"Libby doesn't allow early returns for books that\n"
                        f"have been fulfilled on Kindle. The book will\n"
                        f"automatically return when the loan expires."
                    )
                else:
                    self.show_message("Error", f"Return failed:\n{error_msg}")

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
