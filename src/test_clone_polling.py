#!/usr/bin/env python3
"""
Test the clone polling mechanism to see what's happening
"""
import ssl
import json
import urllib.request
import gzip
import time

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://sentry-read.svc.overdrive.com"

def make_request(endpoint, identity_token):
    """Make a request with proper headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'Referer': 'https://libbyapp.com/',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Authorization': f'Bearer {identity_token}'
    }

    req = urllib.request.Request(f"{BASE_URL}/{endpoint}", headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read()
            if response.headers.get('Content-Encoding') == 'gzip':
                response_data = gzip.decompress(response_data)
            return json.loads(response_data.decode('utf-8')), None
    except urllib.error.HTTPError as e:
        error_body = e.read()
        if e.headers.get('Content-Encoding') == 'gzip':
            error_body = gzip.decompress(error_body)
        error_text = error_body.decode('utf-8')
        return None, f"HTTP {e.code}: {error_text}"
    except Exception as e:
        return None, str(e)

print("=" * 60)
print("Clone Polling Debug Test")
print("=" * 60)

# Step 1: Get chip
print("\n1. Getting identity chip...")
req = urllib.request.Request(
    f"{BASE_URL}/chip?client=dewey",
    method='POST',
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'Referer': 'https://libbyapp.com/',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
)

with urllib.request.urlopen(req) as response:
    response_data = response.read()
    if response.headers.get('Content-Encoding') == 'gzip':
        response_data = gzip.decompress(response_data)
    chip_data = json.loads(response_data.decode('utf-8'))
    identity = chip_data['identity']
    print(f"   ✓ Got identity token: {identity[:30]}...")

# Step 2: Generate clone code
print("\n2. Generating clone code...")
code_data, error = make_request('chip/clone/code', identity)
if error:
    print(f"   ✗ Error: {error}")
    exit(1)

code = code_data['code']
print(f"   ✓ Clone code: {code}")
print(f"\n   Enter this code in your Libby app NOW!")
print(f"   Settings → Copy To Another Device → {code}")
input("\n   Press Enter after entering the code...")

# Step 3: Poll for completion
print("\n3. Polling for authentication completion...")
print("   (Will show detailed error messages)\n")

for attempt in range(1, 91):
    print(f"   Attempt {attempt}/90 ({attempt * 2}s)...", end=" ")

    # Try syncing
    sync_data, error = make_request('chip/sync', identity)

    if sync_data:
        # Check if we have cards
        if 'cards' in sync_data and sync_data['cards']:
            print(f"\n\n   ✓✓✓ SUCCESS! ✓✓✓")
            print(f"   Authentication completed!")
            print(f"   Found {len(sync_data['cards'])} library card(s)")
            print(f"   Response keys: {list(sync_data.keys())}")
            exit(0)
        else:
            print(f"No cards yet. Keys: {list(sync_data.keys())}")
    else:
        print(f"ERROR: {error}")

    time.sleep(2)

print("\n\n   ✗ Timed out after 180 seconds")
