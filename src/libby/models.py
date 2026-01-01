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
        return cls(
            card_id=data.get('cardId', ''),
            library_name=data.get('advantageKey', {}).get('name', 'Unknown Library'),
            advantage_key=data.get('advantageKey', {}).get('key'),
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
            is_locked=data.get('isLocked', False)
        )


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
