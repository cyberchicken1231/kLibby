"""
Libby API Client
Based on reverse-engineered API from odmpy and libby-calibre-plugin
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
import urllib.error
import gzip
from typing import Any
from pathlib import Path
import os

from .models import Card, Loan, Hold, Title


class LibbyClient:
    """Client for interacting with Libby API"""

    BASE_URL = "https://sentry-read.svc.overdrive.com"
    TAGS_URL = "https://vandal.svc.overdrive.com"

    def __init__(self, identity_token: str | None = None, settings_path: str | None = None):
        """
        Initialize Libby client

        Args:
            identity_token: Bearer token for authentication
            settings_path: Path to store settings (defaults to ~/.klibby)
        """
        self.identity_token = identity_token
        self.settings_path = Path(settings_path or os.path.expanduser("~/.klibby"))
        self.settings_path.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_path / "settings.json"

        # Load saved settings if available
        if not identity_token:
            self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from disk"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.identity_token = data.get('identity_token')
            except (json.JSONDecodeError, IOError):
                pass

    def _save_settings(self) -> None:
        """Save settings to disk"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump({
                    'identity_token': self.identity_token
                }, f)
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        base_url: str | None = None,
        return_response: bool = False,
        follow_redirects: bool = True,
        custom_headers: dict[str, str] | None = None
    ) -> Any:
        """
        Make HTTP request to Libby API

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, DELETE)
            params: URL query parameters
            data: Request body data
            base_url: Override base URL
            return_response: If True, return response object instead of parsed JSON
            follow_redirects: If False, don't automatically follow redirects
            custom_headers: Custom headers to merge with defaults

        Returns:
            Parsed JSON response or response object if return_response=True

        Raises:
            urllib.error.HTTPError: On HTTP errors
        """
        url = f"{base_url or self.BASE_URL}/{endpoint.lstrip('/')}"

        # Add query parameters
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        # Prepare default headers - must mimic browser/Libby app to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'Referer': 'https://libbyapp.com/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # Merge custom headers (custom headers take precedence)
        if custom_headers:
            headers.update(custom_headers)

        if self.identity_token:
            headers['Authorization'] = f'Bearer {self.identity_token}'

        # Prepare request body
        request_body = None
        if data:
            if method == 'POST':
                headers['Content-Type'] = 'application/json'
                request_body = json.dumps(data).encode('utf-8')

        # Make request
        req = urllib.request.Request(url, data=request_body, headers=headers, method=method)

        # Custom redirect handler if needed
        if not follow_redirects:
            class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = urllib.request.build_opener(NoRedirectHandler)
            try:
                response = opener.open(req)
                if return_response:
                    return response
                response_data = response.read()
                if response.headers.get('Content-Encoding') == 'gzip':
                    response_data = gzip.decompress(response_data)
                if response_data:
                    return json.loads(response_data.decode('utf-8'))
                return {}
            except urllib.error.HTTPError as e:
                # For redirects, HTTPError is raised with 3xx codes
                if e.code in (301, 302, 303, 307, 308) and return_response:
                    return e
                # Regular error handling
                error_body = e.read()
                if e.headers.get('Content-Encoding') == 'gzip':
                    error_body = gzip.decompress(error_body)
                error_text = error_body.decode('utf-8') if error_body else '(empty response)'

                # Add debug info for 403 errors
                if e.code == 403:
                    error_text += f"\n\nResponse headers: {dict(e.headers)}"
                    error_text += f"\nRequest URL: {url}"

                raise Exception(f"HTTP {e.code}: {error_text}")

        # Normal request with redirects
        try:
            with urllib.request.urlopen(req) as response:
                if return_response:
                    return response

                response_data = response.read()

                # Decompress if gzip-encoded
                if response.headers.get('Content-Encoding') == 'gzip':
                    response_data = gzip.decompress(response_data)

                if response_data:
                    return json.loads(response_data.decode('utf-8'))
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read()

            # Decompress error body if needed
            if e.headers.get('Content-Encoding') == 'gzip':
                error_body = gzip.decompress(error_body)

            error_text = error_body.decode('utf-8') if error_body else '(empty response)'

            # Add debug info for 403 errors
            if e.code == 403:
                error_text += f"\n\nResponse headers: {dict(e.headers)}"
                error_text += f"\nRequest URL: {url}"

            raise Exception(f"HTTP {e.code}: {error_text}")

    def get_chip(self) -> dict[str, Any]:
        """
        Get a new identity chip (anonymous authentication)

        Returns:
            Chip data containing identity token
        """
        # MUST be POST with client=dewey parameter
        response = self._make_request('chip', params={'client': 'dewey'}, method='POST')
        if 'identity' in response:
            self.identity_token = response['identity']
            self._save_settings()
        else:
            raise Exception("Failed to get identity chip from server")
        return response

    def generate_clone_code(self) -> dict[str, Any]:
        """
        Generate an 8-digit setup code for device linking

        This is the NEW Libby authentication flow (2024+):
        1. kLibby generates a code and displays it
        2. User enters this code in the Libby app
        3. kLibby polls to check if authentication completed

        Returns:
            Response containing the clone code and expiration
        """
        # IMPORTANT: Always get a fresh identity token for clone code generation
        # Old/saved tokens may cause "missing_chip" errors
        self.identity_token = None
        chip_response = self.get_chip()

        # Verify we got a token
        if not self.identity_token:
            raise Exception("Failed to get identity token from server. Response: " + str(chip_response))

        # Validate the token looks correct (should be a long string)
        if not isinstance(self.identity_token, str) or len(self.identity_token) < 10:
            raise Exception(f"Invalid identity token received: {self.identity_token}")

        # Generate the code - this requires the identity token in Authorization header
        try:
            response = self._make_request('chip/clone/code')
        except Exception as e:
            error_msg = str(e)
            # Provide more context in the error message
            token_info = ""
            if self.identity_token:
                token_info = (
                    f"\nToken length: {len(self.identity_token)}"
                    f"\nToken prefix: {self.identity_token[:20]}..."
                )
            raise Exception(f"Failed to generate clone code: {error_msg}{token_info}")

        # The response should contain the code
        if 'code' not in response:
            raise Exception(f"No code in response. Keys: {list(response.keys())}, Response: {response}")

        return response

    def clone_by_code(self, code: str) -> dict[str, Any]:
        """
        Link to existing Libby account using 8-digit sync code

        NOTE: As of late 2024, clone codes give READ-ONLY permissions.
        They work for viewing loans/holds/cards but NOT for downloading books.
        Use set_browser_token() instead for download permissions.

        Args:
            code: 8-digit sync code (either FROM Libby or the one YOU generated)

        Returns:
            Chip data with synced identity
        """
        if not self.identity_token:
            self.get_chip()

        # Code goes in request body, not URL path
        response = self._make_request(
            'chip/clone/code',
            method='POST',
            data={'code': code}
        )

        # Response should contain new authenticated identity token
        if 'identity' in response:
            self.identity_token = response['identity']
            self._save_settings()

        return response

    def set_browser_token(self, token: str) -> bool:
        """
        Set identity token manually from browser session

        This is the recommended authentication method for downloads.
        As of late 2024, clone codes only give read-only access.

        To get a browser token:
        1. Go to https://libbyapp.com in a web browser
        2. Sign in with your library card
        3. Open DevTools (F12)
        4. Go to Network tab
        5. Click on any book in Libby
        6. Find a request in the Network tab
        7. Look for the 'Authorization' header
        8. Copy the full value (including 'Bearer ' prefix or not)

        Args:
            token: Full session token from browser (with or without 'Bearer ' prefix)

        Returns:
            True if token was set successfully
        """
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Basic validation
        token = token.strip()
        if not token or len(token) < 50:
            raise ValueError("Token appears invalid (too short). Make sure you copied the full token.")

        # Set and save the token
        self.identity_token = token
        self._save_settings()

        # Verify it works by trying to sync
        try:
            sync_result = self.sync()
            if sync_result.get('result') == 'synchronized':
                return True
            else:
                raise Exception(f"Token set but sync failed: {sync_result}")
        except Exception as e:
            # Token didn't work, clear it
            self.identity_token = None
            self._save_settings()
            raise Exception(f"Browser token verification failed: {e}")

    def verify_clone_status(self) -> dict[str, Any]:
        """
        Check if clone code was used and authentication completed

        Returns:
            Sync state if authenticated, otherwise raises exception
        """
        return self.sync()

    def sync(self) -> dict[str, Any]:
        """
        Sync account state - retrieves cards, loans, holds

        Returns:
            Sync state containing all account information
        """
        if not self.identity_token:
            raise Exception("Not authenticated. Call clone_by_code() first.")

        return self._make_request('chip/sync')

    def get_cards(self) -> list[Card]:
        """
        Get list of library cards

        Returns:
            List of Card objects
        """
        sync_data = self.sync()
        cards = []

        for card_data in sync_data.get('cards', []):
            cards.append(Card.from_api(card_data))

        return cards

    def get_loans(self) -> list[Loan]:
        """
        Get active loans

        Returns:
            List of Loan objects
        """
        sync_data = self.sync()
        loans = []

        for loan_data in sync_data.get('loans', []):
            loans.append(Loan.from_api(loan_data))

        return loans

    def get_holds(self) -> list[Hold]:
        """
        Get active holds

        Returns:
            List of Hold objects
        """
        sync_data = self.sync()
        holds = []

        for hold_data in sync_data.get('holds', []):
            holds.append(Hold.from_api(hold_data))

        return holds

    def borrow_title(
        self,
        card_id: str,
        title_id: str,
        days: int = 21
    ) -> dict[str, Any]:
        """
        Borrow a title

        Args:
            card_id: Library card ID
            title_id: Title ID to borrow
            days: Loan period in days (default 21)

        Returns:
            Loan information
        """
        endpoint = f'card/{card_id}/loan/{title_id}'
        return self._make_request(
            endpoint,
            method='POST',
            data={'days': days}
        )

    def return_loan(self, card_id: str, loan_id: str) -> dict[str, Any]:
        """
        Return a loan early

        Args:
            card_id: Library card ID
            loan_id: Loan ID to return

        Returns:
            Response data
        """
        endpoint = f'card/{card_id}/loan/{loan_id}'
        return self._make_request(endpoint, method='DELETE')

    def get_download_link(
        self,
        card_id: str,
        loan_id: str,
        format_type: str = 'ebook-epub-adobe'
    ) -> tuple[str, str]:
        """
        Get download link for a loaned item

        Args:
            card_id: Library card ID
            loan_id: Loan ID
            format_type: Format type (ebook-epub-adobe, ebook-epub-open, etc.)

        Returns:
            Tuple of (download_url, content_type)
        """
        # Get loan fulfillment info
        endpoint = f'card/{card_id}/loan/{loan_id}/fulfill/{format_type}'
        response = self._make_request(endpoint)

        # Extract download URL
        download_url = response.get('urls', {}).get('web', '')
        content_type = response.get('type', {}).get('id', '')

        return download_url, content_type

    def download_book(
        self,
        card_id: str,
        loan_id: str,
        output_path: str,
        format_type: str = 'ebook-epub-open',
        title_id: str | None = None
    ) -> str:
        """
        Download a book to file

        Args:
            card_id: Library card ID
            loan_id: Loan ID
            output_path: Path to save file
            format_type: Format type (prefer open format if available)
            title_id: Title/reserve ID (optional, will be looked up if not provided)

        Returns:
            Path to downloaded file
        """
        # Step 1: Open the loan (required before fulfill)
        # This API call prepares the loan for download
        if not title_id:
            # Look up title_id from the loan
            loans = self.get_loans()
            matching_loan = next((l for l in loans if l.loan_id == loan_id), None)
            if not matching_loan or not matching_loan.title:
                raise Exception("Could not find title ID for loan")
            title_id = matching_loan.title.title_id

        print(f"\n[DEBUG] Opening loan before fulfill...")
        print(f"  Loan ID: {loan_id}")
        print(f"  Title ID: {title_id}")

        # Determine loan type from format
        if 'audiobook' in format_type:
            loan_type = 'audiobook'
        elif 'magazine' in format_type:
            loan_type = 'magazine'
        else:
            loan_type = 'book'

        # Call open_loan endpoint to prepare for download
        open_endpoint = f'open/{loan_type}/card/{card_id}/title/{title_id}'
        try:
            open_response = self._make_request(open_endpoint)
            print(f"  ✓ Loan opened successfully")
            print(f"  Open response keys: {list(open_response.keys())}")
        except Exception as e:
            print(f"  ✗ Failed to open loan: {e}")
            raise Exception(f"Failed to open loan before fulfill: {e}")

        # Step 2: Now proceed with fulfill request
        # Prepare headers for fulfill request
        # Match odmpy's approach: minimal headers without Referer
        fulfill_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

        # Add auth token
        if self.identity_token:
            fulfill_headers['Authorization'] = f'Bearer {self.identity_token}'

        endpoint = f'card/{card_id}/loan/{loan_id}/fulfill/{format_type}'

        # Debug: print request details
        full_url = f"{self.BASE_URL}/{endpoint}"
        print(f"\n[DEBUG] Fulfill request:")
        print(f"  URL: {full_url}")
        print(f"  Format: {format_type}")
        print(f"  Has auth token: {self.identity_token is not None}")
        print(f"  Headers: {list(fulfill_headers.keys())}")
        if self.identity_token:
            print(f"  Token preview: {self.identity_token[:50]}...")

        # Make fulfill request directly (bypass _make_request to avoid default headers)
        fulfill_url = f"{self.BASE_URL}/{endpoint}"
        fulfill_req = urllib.request.Request(fulfill_url, headers=fulfill_headers, method='GET')

        # For open formats (ebook-epub-open, ebook-pdf-open), the fulfill endpoint
        # returns a redirect to the actual file on a CDN
        if format_type in ('ebook-epub-open', 'ebook-pdf-open'):
            # Get the redirect without following it
            class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = urllib.request.build_opener(NoRedirectHandler)

            try:
                response = opener.open(fulfill_req)
                redirect_url = response.headers.get('Location')
            except urllib.error.HTTPError as e:
                if e.code in (301, 302, 303, 307, 308):
                    # Redirect as expected
                    redirect_url = e.headers.get('Location')
                else:
                    # Real error
                    error_body = e.read().decode('utf-8') if e.read() else '(empty)'
                    raise Exception(f"Fulfill request failed: HTTP {e.code}: {error_body}")

            if not redirect_url:
                raise Exception("Could not get download redirect URL from fulfill endpoint")

            # Download from the redirect URL
            download_req = urllib.request.Request(redirect_url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
            })

            with urllib.request.urlopen(download_req) as download_response:
                with open(output_path, 'wb') as f:
                    f.write(download_response.read())

        else:
            # For DRM formats (ebook-epub-adobe, audiobook-mp3, etc.),
            # the fulfill endpoint returns the file content directly
            try:
                with urllib.request.urlopen(fulfill_req) as response:
                    with open(output_path, 'wb') as f:
                        f.write(response.read())
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if e.read() else '(empty)'
                raise Exception(f"Fulfill request failed: HTTP {e.code}: {error_body}\n\nHeaders sent: {list(fulfill_headers.keys())}")

        return output_path

    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.identity_token is not None

    def clear_auth(self) -> None:
        """Clear authentication"""
        self.identity_token = None
        if self.settings_file.exists():
            self.settings_file.unlink()
