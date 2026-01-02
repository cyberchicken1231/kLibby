"""
Libby API Client
Based on reverse-engineered API from odmpy and libby-calibre-plugin
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
import urllib.error
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
        base_url: str | None = None
    ) -> Any:
        """
        Make HTTP request to Libby API

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, DELETE)
            params: URL query parameters
            data: Request body data
            base_url: Override base URL

        Returns:
            Parsed JSON response

        Raises:
            urllib.error.HTTPError: On HTTP errors
        """
        url = f"{base_url or self.BASE_URL}/{endpoint.lstrip('/')}"

        # Add query parameters
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        # Prepare request
        headers = {
            'User-Agent': 'kLibby/0.1.0',
            'Accept': 'application/json'
        }

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

        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                if response_data:
                    return json.loads(response_data.decode('utf-8'))
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            raise Exception(f"HTTP {e.code}: {error_body}")

    def get_chip(self) -> dict[str, Any]:
        """
        Get a new identity chip (anonymous authentication)

        Returns:
            Chip data containing identity token
        """
        response = self._make_request('chip')
        if 'identity' in response:
            self.identity_token = response['identity']
            self._save_settings()
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
        # IMPORTANT: Must have an identity token first
        if not self.identity_token:
            self.get_chip()

        # Generate the code
        response = self._make_request('chip/clone/code')

        # Save the identity token from the response
        if 'identity' in response:
            self.identity_token = response['identity']
            self._save_settings()

        return response

    def clone_by_code(self, code: str) -> dict[str, Any]:
        """
        Link to existing Libby account using 8-digit sync code

        DEPRECATED: This is the OLD flow where Libby gave you a code.
        Use generate_clone_code() for the NEW flow (2024+).

        Args:
            code: 8-digit sync code from Libby app

        Returns:
            Chip data with synced identity
        """
        if not self.identity_token:
            self.get_chip()

        response = self._make_request(
            f'chip/clone/code/{code}',
            method='POST'
        )

        if 'identity' in response:
            self.identity_token = response['identity']
            self._save_settings()

        return response

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
        format_type: str = 'ebook-epub-open'
    ) -> str:
        """
        Download a book to file

        Args:
            card_id: Library card ID
            loan_id: Loan ID
            output_path: Path to save file
            format_type: Format type (prefer open format if available)

        Returns:
            Path to downloaded file
        """
        download_url, content_type = self.get_download_link(card_id, loan_id, format_type)

        if not download_url:
            raise Exception("Could not get download URL")

        # Download file
        req = urllib.request.Request(download_url, headers={
            'User-Agent': 'kLibby/0.1.0'
        })

        with urllib.request.urlopen(req) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())

        return output_path

    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.identity_token is not None

    def clear_auth(self) -> None:
        """Clear authentication"""
        self.identity_token = None
        if self.settings_file.exists():
            self.settings_file.unlink()
