#!/usr/bin/env python3
"""
Test authentication flow step by step
"""
import ssl
import json
import urllib.request

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://sentry-read.svc.overdrive.com"

print("=" * 60)
print("Testing Libby Authentication Flow")
print("=" * 60)

# Step 1: Get initial chip
print("\n1. Getting anonymous identity chip...")
try:
    req = urllib.request.Request(
        f"{BASE_URL}/chip",
        headers={'User-Agent': 'kLibby/0.1.0'}
    )
    with urllib.request.urlopen(req) as response:
        chip_data = json.loads(response.read().decode('utf-8'))
        print(f"   SUCCESS: Got chip response")
        print(f"   Keys in response: {list(chip_data.keys())}")

        if 'identity' in chip_data:
            identity = chip_data['identity']
            print(f"   Identity token: {identity[:50]}..." if len(identity) > 50 else f"   Identity token: {identity}")
        else:
            print("   ERROR: No 'identity' in chip response!")
            print(f"   Full response: {chip_data}")
            exit(1)

except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Step 2: Generate clone code using the identity
print("\n2. Generating clone code with identity token...")
try:
    req = urllib.request.Request(
        f"{BASE_URL}/chip/clone/code",
        headers={
            'User-Agent': 'kLibby/0.1.0',
            'Authorization': f'Bearer {identity}'
        }
    )
    with urllib.request.urlopen(req) as response:
        code_data = json.loads(response.read().decode('utf-8'))
        print(f"   SUCCESS: Got clone code response")
        print(f"   Keys in response: {list(code_data.keys())}")

        if 'code' in code_data:
            code = code_data['code']
            print(f"   Clone code: {code}")
        else:
            print("   ERROR: No 'code' in response!")
            print(f"   Full response: {code_data}")

except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"   ERROR: HTTP {e.code}")
    print(f"   Response: {error_body}")
    exit(1)
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

print("\n" + "=" * 60)
print("Authentication test completed successfully!")
print("=" * 60)
print("\nThe API is working. The issue might be in how kLibby")
print("is making the requests. Check the client code.")
