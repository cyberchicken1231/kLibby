#!/usr/bin/env python3
"""
Detailed authentication debugging
Shows exactly what's being sent and received
"""
import ssl
import json
import urllib.request
import gzip

# Disable SSL verification (Kindle has outdated CA certificates)
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://sentry-read.svc.overdrive.com"

print("\n" + "=" * 60)
print("  Authentication Debug Test")
print("=" * 60 + "\n")

# Step 1: Get initial chip
print("Step 1: Getting identity chip...")
print(f"  URL: {BASE_URL}/chip?client=dewey")
print("  Method: POST")
print("  Headers:")
print("    User-Agent: Mozilla/5.0 (Macintosh; ...)")
print("    Accept: application/json")
print("    Referer: https://libbyapp.com/")

try:
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

        # Decompress if gzip-encoded
        if response.headers.get('Content-Encoding') == 'gzip':
            response_data = gzip.decompress(response_data)

        chip_data = json.loads(response_data.decode('utf-8'))

        print(f"\n  Response Status: {response.status}")
        print(f"  Response Keys: {list(chip_data.keys())}")

        if 'identity' in chip_data:
            identity = chip_data['identity']
            print(f"  ✓ Got identity token")
            print(f"  Token length: {len(identity)}")
            print(f"  Token prefix: {identity[:20]}...")
            print(f"  Token suffix: ...{identity[-20:]}")
        else:
            print(f"  ✗ No identity in response!")
            print(f"  Full response: {chip_data}")
            exit(1)

except Exception as e:
    print(f"\n  ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Generate clone code
print("\n" + "-" * 60)
print("\nStep 2: Generating clone code...")
print(f"  URL: {BASE_URL}/chip/clone/code")
print("  Method: GET")
print("  Headers:")
print("    User-Agent: kLibby/0.1.0")
print(f"    Authorization: Bearer {identity[:20]}...{identity[-10:]}")

try:
    req = urllib.request.Request(
        f"{BASE_URL}/chip/clone/code",
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'Referer': 'https://libbyapp.com/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Authorization': f'Bearer {identity}'
        }
    )

    with urllib.request.urlopen(req) as response:
        response_data = response.read()

        # Decompress if gzip-encoded
        if response.headers.get('Content-Encoding') == 'gzip':
            response_data = gzip.decompress(response_data)

        code_data = json.loads(response_data.decode('utf-8'))

        print(f"\n  Response Status: {response.status}")
        print(f"  Response Keys: {list(code_data.keys())}")

        if 'code' in code_data:
            code = code_data['code']
            print(f"  ✓ SUCCESS! Got code: {code}")
            print("\n  Enter this code in your Libby app:")
            print(f"  Settings → Copy To Another Device → {code}")
        else:
            print(f"  ✗ No code in response!")
            print(f"  Full response: {code_data}")

except urllib.error.HTTPError as e:
    print(f"\n  ✗ HTTP ERROR {e.code}")
    error_body = e.read()

    # Decompress error body if needed
    if e.headers.get('Content-Encoding') == 'gzip':
        error_body = gzip.decompress(error_body)

    error_text = error_body.decode('utf-8')
    print(f"  Error body: {error_text}")

    # Try to parse error
    try:
        error_data = json.loads(error_text)
        print(f"  Error result: {error_data.get('result', 'unknown')}")
    except:
        pass

    import traceback
    traceback.print_exc()
    exit(1)

except Exception as e:
    print(f"\n  ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("  Test Complete")
print("=" * 60 + "\n")
