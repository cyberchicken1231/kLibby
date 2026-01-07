#!/usr/bin/env python3
"""
Test download flow to diagnose missing_chip error
Shows detailed info at each step
"""
import ssl
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

from libby.client import LibbyClient

print("=" * 60)
print("  Download Flow Debug Test")
print("=" * 60)

# Step 1: Load client with saved credentials
print("\n1. Loading saved credentials...")
client = LibbyClient()

if not client.identity_token:
    print("   ✗ ERROR: Not authenticated!")
    print("   Please authenticate first using the main app.")
    exit(1)

print(f"   ✓ Identity token loaded")
print(f"   Token length: {len(client.identity_token)}")
print(f"   Token prefix: {client.identity_token[:30]}...")

# Step 2: Sync and get loans
print("\n2. Syncing account and getting loans...")
try:
    sync_data = client.sync()
    print(f"   ✓ Sync successful")
    print(f"   Sync result: {sync_data.get('result', 'unknown')}")

    cards = sync_data.get('cards', [])
    loans = sync_data.get('loans', [])

    print(f"   Cards found: {len(cards)}")
    print(f"   Loans found: {len(loans)}")

    if not loans:
        print("\n   No loans to test. Please checkout a book first.")
        exit(0)

    # Show ALL loans with format status
    print(f"\n3. All loans ({len(loans)} total):")
    for i, loan in enumerate(loans, 1):
        title = loan.get('title', 'Unknown')
        is_format_locked = loan.get('isFormatLockedIn', False)

        # Check what format is locked
        locked_format = "None"
        if is_format_locked:
            for fmt in loan.get('formats', []):
                if fmt.get('isLockedIn', False):
                    locked_format = fmt.get('id', 'Unknown')
                    break

        lock_status = f"LOCKED to {locked_format}" if is_format_locked else "unlocked ✓"
        print(f"   {i}. {title}")
        print(f"      Status: {lock_status}")
        print()

    # Find first non-Kindle-locked book
    test_loan = None
    for loan in loans:
        is_format_locked = loan.get('isFormatLockedIn', False)
        if not is_format_locked:
            test_loan = loan
            print(f"   → Testing first unlocked book: {loan.get('title', 'Unknown')}")
            break

        # Check if it's Kindle-locked
        is_kindle = False
        for fmt in loan.get('formats', []):
            if fmt.get('id', '').startswith('ebook-kindle') and fmt.get('isLockedIn', False):
                is_kindle = True
                break

        if not is_kindle:
            test_loan = loan
            print(f"   → Testing first non-Kindle book: {loan.get('title', 'Unknown')}")
            break

    if not test_loan:
        print(f"\n   ⚠ All books are Kindle-locked!")
        print(f"   Testing first book anyway to show the error...")
        test_loan = loans[0]

    print(f"\n4. Examining selected loan structure...")
    print(f"   Loan ID: {test_loan.get('id', 'MISSING')}")
    print(f"   Card ID: {test_loan.get('cardId', 'MISSING')}")
    print(f"   Title: {test_loan.get('title', 'Unknown')}")
    print(f"   Format locked: {test_loan.get('isFormatLockedIn', False)}")

    # Check if IDs are present
    loan_id = test_loan.get('id', '')
    card_id = test_loan.get('cardId', '')

    if not loan_id:
        print("\n   ✗ ERROR: Loan is missing 'id' field!")
        print(f"   Full loan data: {json.dumps(test_loan, indent=2)}")
        exit(1)

    if not card_id:
        print("\n   ✗ ERROR: Loan is missing 'cardId' field!")
        print(f"   Full loan data: {json.dumps(test_loan, indent=2)}")
        exit(1)

    print(f"\n   ✓ Loan IDs are present")

    # Step 5: Try to get download link
    print(f"\n5. Attempting to get download link...")
    print(f"   Card ID: {card_id}")
    print(f"   Loan ID: {loan_id}")
    print(f"   Format: ebook-epub-open")

    try:
        download_url, content_type = client.get_download_link(
            card_id,
            loan_id,
            'ebook-epub-open'
        )

        print(f"\n   ✓✓✓ SUCCESS! ✓✓✓")
        print(f"   Download URL: {download_url[:50]}..." if download_url else "   Download URL: EMPTY")
        print(f"   Content type: {content_type}")

    except Exception as e:
        error_msg = str(e)
        print(f"\n   ✗✗✗ FAILED! ✗✗✗")
        print(f"   Error: {error_msg}")

        # Try alternative format
        print(f"\n5. Trying alternative format (ebook-epub-adobe)...")
        try:
            download_url, content_type = client.get_download_link(
                card_id,
                loan_id,
                'ebook-epub-adobe'
            )

            print(f"\n   ✓ Alternative format worked!")
            print(f"   Download URL: {download_url[:50]}..." if download_url else "   Download URL: EMPTY")
            print(f"   Content type: {content_type}")

        except Exception as e2:
            print(f"\n   ✗ Alternative format also failed: {str(e2)}")

            # Show full loan data for debugging
            print(f"\n   Full loan data:")
            print(json.dumps(test_loan, indent=2))

except Exception as e:
    print(f"\n   ✗ ERROR during sync: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("  Test Complete")
print("=" * 60)
