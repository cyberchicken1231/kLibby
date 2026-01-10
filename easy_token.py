#!/usr/bin/env python3
"""
Easy browser token extraction - YOU do the clicking, we capture the token!
"""

import json
import time
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from libby.client import LibbyClient


def extract_token_easy():
    """
    Open browser, let user login manually, capture Authorization token automatically
    """
    print("=" * 60)
    print("EASY TOKEN EXTRACTION")
    print("=" * 60)
    print("\nHow this works:")
    print("1. We'll open a Chrome window to libbyapp.com")
    print("2. YOU manually sign in with your library card")
    print("3. YOU click on any book in your shelf")
    print("4. We automatically capture the Authorization token")
    print("5. Token gets saved to kLibby - done!")
    print("\nPress Enter when ready...")
    input()

    # Configure Chrome to capture network logs
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    print("\n🌐 Opening Chrome browser...")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Go to Libby
        driver.get("https://libbyapp.com")

        print("\n✋ NOW IT'S YOUR TURN!")
        print("=" * 60)
        print("In the browser window that just opened:")
        print("  1. Search for your library")
        print("  2. Click 'Sign In with library card'")
        print("  3. Enter your card number and PIN")
        print("  4. Click on ANY book in your shelf")
        print("\nThen come back here and press Enter...")
        print("=" * 60)

        input("\nPress Enter AFTER you've signed in and clicked a book: ")

        print("\n🔍 Now searching for your token in network logs...")
        print("(Give it a few seconds...)")
        time.sleep(2)

        # Monitor network logs for Authorization token
        token = None
        start_time = time.time()
        timeout = 300  # 5 minutes timeout

        while not token and (time.time() - start_time) < timeout:
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
                        url = request.get('url', '')

                        # Only look at requests to Libby API
                        if 'overdrive.com' in url or 'libbyapp.com' in url:
                            # Check if Authorization header exists
                            auth_header = headers.get('Authorization') or headers.get('authorization')
                            if auth_header and 'Bearer' in auth_header:
                                # Extract token (remove 'Bearer ' prefix)
                                extracted = auth_header.replace('Bearer ', '').strip()
                                if len(extracted) > 100:  # Valid tokens are long
                                    # Validate token has linked accounts (not anonymous)
                                    try:
                                        import base64
                                        parts = extracted.split('.')
                                        if len(parts) == 3:
                                            payload = parts[1]
                                            padding = 4 - len(payload) % 4
                                            if padding != 4:
                                                payload += '=' * padding
                                            decoded = base64.b64decode(payload).decode('utf-8')
                                            token_data = json.loads(decoded)
                                            accounts = token_data.get('chip', {}).get('accounts', [])

                                            # Only accept tokens with linked library accounts
                                            if accounts and len(accounts) > 0:
                                                token = extracted
                                                print(f"\n✓ FOUND IT! Token captured (length: {len(token)})")
                                                print(f"  ✓ Linked accounts: {len(accounts)}")
                                                break
                                            else:
                                                print(f"  ⊘ Skipping token (no linked accounts - not signed in yet)")
                                    except Exception:
                                        pass  # Skip invalid tokens
                except (json.JSONDecodeError, KeyError):
                    continue

            time.sleep(0.5)  # Check twice per second

        if not token:
            print("\n✗ Timeout: No token found after 5 minutes")
            print("Make sure you clicked on a book in your shelf!")
            return False

        # Decode and show token info
        print("\n📋 Token Information:")
        try:
            import base64
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.b64decode(payload).decode('utf-8')
                token_data = json.loads(decoded)

                print(f"  - Issuer: {token_data.get('iss', 'unknown')}")
                print(f"  - Chip ID: {token_data.get('chip', {}).get('id', 'unknown')}")

                exp = token_data.get('exp', 0)
                if exp:
                    exp_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
                    print(f"  - Expires: {exp_date}")
        except Exception:
            pass

        # Save to kLibby
        print("\n💾 Saving token to kLibby...")
        client = LibbyClient()

        print(f"  Settings file: {client.settings_file}")
        print(f"  Token preview: {token[:50]}...")

        client.set_browser_token(token, verify=False)

        # Verify it was saved
        import base64
        saved_token = client.identity_token
        if saved_token == token:
            parts = saved_token.split('.')
            payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
            decoded_saved = json.loads(base64.b64decode(payload))
            print(f"  ✓ Token saved successfully!")
            print(f"  ✓ Saved chip ID: {decoded_saved['chip']['id']}")
            print(f"  ✓ Saved accounts: {decoded_saved['chip']['accounts']}")
        else:
            print(f"  ✗ WARNING: Token mismatch after save!")

        print("\n✅ SUCCESS! Token saved to kLibby!")
        print("\nYou can now:")
        print("  - Close the browser window")
        print("  - Run: ./klibby.sh")
        print("  - Download books!")

        input("\nPress Enter to close browser...")
        return True

    finally:
        driver.quit()
        print("\n👋 Browser closed. All done!")


if __name__ == '__main__':
    try:
        success = extract_token_easy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
