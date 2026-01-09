#!/usr/bin/env python3
"""
Automated browser token extraction using Selenium
Logs into libbyapp.com and captures the Authorization token
"""

import json
import time
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
from libby.client import LibbyClient


class TokenRefresher:
    """Automatically refresh Libby browser token"""

    def __init__(self, settings_path: str | None = None):
        self.settings_path = Path(settings_path or Path.home() / ".klibby")
        self.settings_path.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.settings_path / "credentials.json"
        self.client = LibbyClient()

    def save_credentials(self, card_number: str, pin: str) -> None:
        """Save library credentials (PLAIN TEXT - be careful!)"""
        data = {
            "card_number": card_number,
            "pin": pin
        }
        with open(self.credentials_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Credentials saved to {self.credentials_file}")
        print("⚠ WARNING: Credentials are stored in PLAIN TEXT!")

    def load_credentials(self) -> tuple[str, str]:
        """Load saved credentials"""
        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"No credentials found at {self.credentials_file}\n"
                "Run this script with --setup first"
            )

        with open(self.credentials_file, 'r') as f:
            data = json.load(f)

        return data['card_number'], data['pin']

    def extract_token_from_browser(self, card_number: str, pin: str, headless: bool = True) -> str:
        """
        Use Selenium to login to libbyapp.com and extract Authorization token

        Args:
            card_number: Library card number
            pin: Library card PIN
            headless: Run browser in headless mode (default True)

        Returns:
            Authorization token (without 'Bearer ' prefix)

        Raises:
            Exception: If login fails or token cannot be extracted
        """
        print("🌐 Starting browser automation...")

        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Enable Network logging to capture requests
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        driver = None
        try:
            # Initialize Chrome driver
            print("  → Launching Chrome...")
            driver = webdriver.Chrome(options=chrome_options)

            # Go to Libby
            print("  → Navigating to libbyapp.com...")
            driver.get("https://libbyapp.com")

            # Wait for page to load
            print("  → Waiting for page to load...")
            wait = WebDriverWait(driver, 20)
            time.sleep(3)

            # Click "Sign in with a library card" button
            print("  → Looking for sign-in button...")

            # Try multiple selectors for the sign-in button
            sign_in_clicked = False
            sign_in_selectors = [
                (By.XPATH, "//button[contains(., 'Sign In')]"),
                (By.XPATH, "//a[contains(., 'Sign In')]"),
                (By.XPATH, "//*[contains(text(), 'library card')]"),
                (By.CSS_SELECTOR, "button[data-test='sign-in']"),
                (By.CSS_SELECTOR, "a[href*='card']"),
                (By.LINK_TEXT, "Sign In"),
                (By.PARTIAL_LINK_TEXT, "library"),
            ]

            for by_method, selector in sign_in_selectors:
                try:
                    sign_in_btn = wait.until(EC.element_to_be_clickable((by_method, selector)))
                    sign_in_btn.click()
                    sign_in_clicked = True
                    print(f"  → Clicked sign-in button using {selector}")
                    break
                except (TimeoutException, WebDriverException):
                    continue

            if not sign_in_clicked:
                print("  → Couldn't find sign-in button, looking for login form directly...")

            time.sleep(3)

            # Find and fill library card input
            print("  → Looking for library card input field...")
            card_input_selectors = [
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[type='tel']"),
                (By.CSS_SELECTOR, "input[name='card']"),
                (By.CSS_SELECTOR, "input[placeholder*='card' i]"),
                (By.CSS_SELECTOR, "input[id*='card' i]"),
                (By.XPATH, "//input[@type='text']"),
                (By.XPATH, "//input[@type='tel']"),
                (By.XPATH, "//input[contains(@placeholder, 'card')]"),
                (By.XPATH, "//input[contains(@placeholder, 'Card')]"),
            ]

            card_input = None
            for by_method, selector in card_input_selectors:
                try:
                    card_input = wait.until(EC.presence_of_element_located((by_method, selector)))
                    print(f"  → Found card input using {selector}")
                    break
                except TimeoutException:
                    continue

            if not card_input:
                # Save screenshot for debugging
                screenshot_path = "/tmp/libby_debug.png"
                driver.save_screenshot(screenshot_path)
                raise Exception(
                    f"Could not find library card input field.\n"
                    f"Screenshot saved to {screenshot_path}\n"
                    f"Try running with --no-headless to see what's happening."
                )

            card_input.clear()
            card_input.send_keys(card_number)
            time.sleep(1)

            # Find and fill PIN input
            print("  → Looking for PIN input field...")
            pin_input_selectors = [
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[name='pin']"),
                (By.CSS_SELECTOR, "input[placeholder*='PIN' i]"),
                (By.CSS_SELECTOR, "input[id*='pin' i]"),
                (By.XPATH, "//input[@type='password']"),
                (By.XPATH, "//input[contains(@placeholder, 'PIN')]"),
                (By.XPATH, "//input[contains(@placeholder, 'pin')]"),
            ]

            pin_input = None
            for by_method, selector in pin_input_selectors:
                try:
                    pin_input = wait.until(EC.presence_of_element_located((by_method, selector)))
                    print(f"  → Found PIN input using {selector}")
                    break
                except TimeoutException:
                    continue

            if not pin_input:
                screenshot_path = "/tmp/libby_debug_pin.png"
                driver.save_screenshot(screenshot_path)
                raise Exception(
                    f"Could not find PIN input field.\n"
                    f"Screenshot saved to {screenshot_path}"
                )

            pin_input.clear()
            pin_input.send_keys(pin)
            time.sleep(1)

            # Click submit button
            print("  → Looking for submit button...")
            submit_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button[data-test*='submit' i]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(., 'Sign In')]"),
                (By.XPATH, "//button[contains(., 'Log In')]"),
                (By.XPATH, "//input[@type='submit']"),
            ]

            submit_clicked = False
            for by_method, selector in submit_selectors:
                try:
                    submit_btn = wait.until(EC.element_to_be_clickable((by_method, selector)))
                    submit_btn.click()
                    print(f"  → Clicked submit button using {selector}")
                    submit_clicked = True
                    break
                except (TimeoutException, WebDriverException):
                    continue

            if not submit_clicked:
                print("  → Warning: Couldn't find submit button, trying Enter key...")
                from selenium.webdriver.common.keys import Keys
                pin_input.send_keys(Keys.RETURN)

            # Wait for login to complete
            print("  → Waiting for login to complete...")
            time.sleep(5)

            # Extract Authorization token from network logs
            print("  → Extracting Authorization token from network requests...")
            token = None

            # Get performance logs
            logs = driver.get_log('performance')

            for log in logs:
                try:
                    log_message = json.loads(log['message'])
                    message = log_message.get('message', {})

                    # Look for network request
                    if message.get('method') == 'Network.requestWillBeSent':
                        request = message.get('params', {}).get('request', {})
                        headers = request.get('headers', {})

                        # Check if Authorization header exists
                        auth_header = headers.get('Authorization') or headers.get('authorization')
                        if auth_header and 'Bearer' in auth_header:
                            # Extract token (remove 'Bearer ' prefix)
                            token = auth_header.replace('Bearer ', '').strip()
                            if len(token) > 100:  # Valid tokens are long
                                print(f"  ✓ Found token (length: {len(token)})")
                                break
                except (json.JSONDecodeError, KeyError):
                    continue

            if not token:
                raise Exception(
                    "Could not extract Authorization token from network logs.\n"
                    "This might mean:\n"
                    "  1. Login failed (wrong credentials)\n"
                    "  2. Libby's interface changed\n"
                    "  3. Network logging didn't capture the token\n"
                    "Try running with --no-headless to see what's happening."
                )

            return token

        finally:
            if driver:
                driver.quit()
                print("  → Browser closed")

    def refresh_token(self, headless: bool = True) -> bool:
        """
        Refresh the token using saved credentials

        Args:
            headless: Run browser in headless mode (default True)

        Returns:
            True if token was refreshed successfully
        """
        print("🔄 Starting token refresh...\n")

        # Load credentials
        try:
            card_number, pin = self.load_credentials()
            print(f"✓ Loaded credentials for card: {card_number[:4]}****{card_number[-4:]}\n")
        except FileNotFoundError as e:
            print(f"✗ {e}")
            return False

        # Extract token
        try:
            token = self.extract_token_from_browser(card_number, pin, headless=headless)
        except Exception as e:
            print(f"\n✗ Failed to extract token: {e}")
            return False

        # Set token in kLibby (without verification since we just got it from browser)
        print("\n💾 Saving token to kLibby...")
        try:
            self.client.set_browser_token(token, verify=False)
            print("✓ Token saved successfully!")

            # Decode and show expiration
            import base64
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.b64decode(payload).decode('utf-8')
                token_data = json.loads(decoded)
                exp = token_data.get('exp', 0)
                if exp:
                    exp_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
                    print(f"✓ Token expires: {exp_date}")

            return True

        except Exception as e:
            print(f"✗ Failed to save token: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Automatically refresh Libby browser token',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First time setup - save credentials
  python3 auto_refresh_token.py --setup

  # Refresh token using saved credentials
  python3 auto_refresh_token.py

  # Refresh token with visible browser (for debugging)
  python3 auto_refresh_token.py --no-headless

  # Set up as a cron job to run daily
  crontab -e
  # Add: 0 3 * * * /usr/bin/python3 /path/to/auto_refresh_token.py
        """
    )

    parser.add_argument(
        '--setup',
        action='store_true',
        help='Save library card credentials'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (for debugging)'
    )

    args = parser.parse_args()

    refresher = TokenRefresher()

    if args.setup:
        print("=== Credential Setup ===\n")
        print("⚠ WARNING: Credentials will be stored in PLAIN TEXT")
        print(f"Location: {refresher.credentials_file}\n")

        card_number = input("Library card number: ").strip()
        pin = input("Library card PIN: ").strip()

        if not card_number or not pin:
            print("✗ Card number and PIN are required")
            sys.exit(1)

        refresher.save_credentials(card_number, pin)
        print("\n✓ Setup complete! Run without --setup to refresh token.")

    else:
        headless = not args.no_headless
        success = refresher.refresh_token(headless=headless)

        if success:
            print("\n✅ Token refresh complete! kLibby is ready to use.")
            sys.exit(0)
        else:
            print("\n❌ Token refresh failed. See errors above.")
            sys.exit(1)


if __name__ == '__main__':
    main()
