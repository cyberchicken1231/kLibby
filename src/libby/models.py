"""
Data models for Libby API entities
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from datetime import datetime


@dataclass
class Card:
    """Represents a library card"""
    card_id: str
    library_name: str
    advantage_key: str | None = None
    username: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Card:
        """Create Card from API response"""
        # advantageKey is a string ID, not a nested object
        # Library info is in a separate 'library' field if present
        library_info = data.get('library', {})
        library_name = library_info.get('name', 'Unknown Library') if isinstance(library_info, dict) else 'Unknown Library'

        return cls(
            card_id=data.get('cardId', ''),
            library_name=library_name,
            advantage_key=data.get('advantageKey'),
            username=data.get('username')
        )


@dataclass
class Title:
    """Represents a book/audiobook title"""
    title_id: str
    title: str
    subtitle: str | None = None
    authors: list[str] = field(default_factory=list)
    cover_url: str | None = None
    format_type: str | None = None  # ebook, audiobook, magazine

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Title:
        """Create Title from API response"""
        authors = []
        if 'firstCreatorName' in data:
            authors.append(data['firstCreatorName'])

        return cls(
            title_id=data.get('id', ''),
            title=data.get('title', 'Unknown Title'),
            subtitle=data.get('subtitle'),
            authors=authors,
            cover_url=data.get('covers', {}).get('cover510Wide', {}).get('href'),
            format_type=data.get('type', {}).get('id')
        )


@dataclass
class Loan:
    """Represents an active loan"""
    loan_id: str
    card_id: str
    title: Title | None
    expire_date: datetime | None = None
    is_locked: bool = False
    is_format_locked_in: bool = False
    is_returnable: bool = True
    formats: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Loan:
        """Create Loan from API response"""
        expire_date = None
        if 'expireDate' in data:
            try:
                expire_date = datetime.fromisoformat(data['expireDate'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        return cls(
            loan_id=data.get('id', ''),
            card_id=data.get('cardId', ''),
            title=Title.from_api(data) if 'title' in data else None,
            expire_date=expire_date,
            is_locked=data.get('isLocked', False),
            is_format_locked_in=data.get('isFormatLockedIn', False),
            is_returnable=data.get('isReturnable', True),
            formats=data.get('formats', [])
        )

    def is_kindle_locked(self) -> bool:
        """Check if loan is locked to Kindle format"""
        if not self.is_format_locked_in:
            return False

        # Check if any Kindle format is locked
        for fmt in self.formats:
            if fmt.get('id', '').startswith('ebook-kindle') and fmt.get('isLockedIn', False):
                return True

        return False

    def get_best_format(self, prefer_open: bool = True) -> str | None:
        """
        Auto-detect the best downloadable format for this loan

        Args:
            prefer_open: If True, prefer DRM-free formats over DRM formats

        Returns:
            Format ID string (e.g., 'ebook-epub-open') or None if no downloadable format

        Raises:
            ValueError: If loan is locked to a non-downloadable format
        """
        # List of downloadable formats
        DOWNLOADABLE_FORMATS = [
            'ebook-epub-open',
            'ebook-pdf-open',
            'ebook-epub-adobe',
            'ebook-pdf-adobe',
            'audiobook-mp3',
            'magazine-overdrive'
        ]

        # If format is locked, check if it's downloadable
        if self.is_format_locked_in:
            for fmt in self.formats:
                if fmt.get('isLockedIn', False):
                    locked_format = fmt.get('id', '')
                    if locked_format in DOWNLOADABLE_FORMATS:
                        return locked_format
                    else:
                        raise ValueError(
                            f'Loan is locked to non-downloadable format "{locked_format}". '
                            f'This format cannot be downloaded (e.g., Kindle, Kobo, OverDrive Read).'
                        )

        # Not locked - choose best available format based on preference
        if prefer_open:
            # Prefer DRM-free formats first
            preferred_order = [
                'ebook-epub-open',
                'ebook-pdf-open',
                'ebook-epub-adobe',
                'ebook-pdf-adobe',
                'audiobook-mp3',
                'magazine-overdrive'
            ]
        else:
            # Prefer DRM formats (useful for testing or certain readers)
            preferred_order = [
                'ebook-epub-adobe',
                'ebook-pdf-adobe',
                'ebook-epub-open',
                'ebook-pdf-open',
                'audiobook-mp3',
                'magazine-overdrive'
            ]

        # Find first available format in preferred order
        available_format_ids = {fmt.get('id', '') for fmt in self.formats}

        for preferred_fmt in preferred_order:
            if preferred_fmt in available_format_ids:
                return preferred_fmt

        return None

    def has_format(self, format_id: str) -> bool:
        """Check if this loan has a specific format available"""
        return any(fmt.get('id') == format_id for fmt in self.formats)


@dataclass
class Hold:
    """Represents a hold on a title"""
    hold_id: str
    card_id: str
    title: Title | None
    available: bool = False

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Hold:
        """Create Hold from API response"""
        return cls(
            hold_id=data.get('id', ''),
            card_id=data.get('cardId', ''),
            title=Title.from_api(data) if 'title' in data else None,
            available=data.get('isAvailable', False)
        )
