# New Libby Authentication Flow (2024+)

## What Changed

In 2024, Libby updated their authentication flow for security improvements. The direction of the code was reversed:

### OLD Flow (deprecated)
1. User opens Libby app
2. Libby **shows** an 8-digit code
3. User enters that code in the new device (kLibby)

### NEW Flow (current)
1. New device (kLibby) **generates** an 8-digit code
2. kLibby displays the code on screen
3. User enters that code in the Libby app
4. kLibby automatically detects when authentication completes

## How It Works in kLibby

### Step-by-Step Process

1. **Launch kLibby** and select "Connect to Libby"

2. **kLibby generates a code**:
   ```
   ═══════════════════════════════
       1234 - 5678
   ═══════════════════════════════
   ```

3. **On your phone/tablet**:
   - Open Libby app
   - Go to Settings (⋮)
   - Select "Copy To Another Device"
   - When prompted, **enter** the code: `1234-5678`

4. **kLibby automatically waits**:
   - Polls every 2 seconds
   - Checks if you entered the code
   - Shows success when authenticated

5. **Done!** Start browsing books

## Technical Implementation

### API Endpoints Used

```python
# 1. Generate code
GET https://sentry-read.svc.overdrive.com/chip/clone/code
Response: {"code": "12345678", "expiration": "..."}

# 2. Poll for authentication (every 2 seconds)
GET https://sentry-read.svc.overdrive.com/chip/sync
Response: {"cards": [...], ...} when successful
```

### Code Flow

```python
# In LibbyClient:
response = client.generate_clone_code()
code = response['code']  # e.g., "12345678"

# Display code to user
print(f"Enter this code in Libby: {code}")

# Poll for completion
while not authenticated:
    sync_data = client.verify_clone_status()
    if sync_data.get('cards'):
        # Success!
        break
    time.sleep(2)
```

### Timeout

- **Polling interval**: 2 seconds
- **Max attempts**: 30 (1 minute total)
- **What happens on timeout**: User can try again

## Why This Change?

### Security Benefits

1. **Code is ephemeral** - Expires quickly
2. **Server-side validation** - Code validated on Libby servers
3. **Better control** - Libby app controls authorization
4. **Prevents replay attacks** - Each code is single-use

### User Experience

- **Clearer flow**: One device generates, one enters
- **Less confusion**: No ambiguity about code direction
- **Automatic detection**: No manual "I'm done" step
- **Better error handling**: Clear timeout messages

## Backward Compatibility

The old `clone_by_code()` method is kept but deprecated:

```python
# OLD method (still works if Libby supports it)
client.clone_by_code("12345678")

# NEW method (recommended)
response = client.generate_clone_code()
code = response['code']
# User enters code in Libby app
# kLibby polls automatically
```

## Troubleshooting

### "Timeout - Code may have expired"

**Problem**: Authentication didn't complete in 1 minute

**Solutions**:
- Try again - generate a new code
- Make sure you entered the code correctly in Libby
- Check internet connection on both devices

### "Failed to generate code"

**Problem**: Can't get initial anonymous identity chip

**Solutions**:
- Check internet connection
- Verify Kindle's date/time is correct
- Try restarting kLibby

### "Authentication failed"

**Problem**: General authentication error

**Solutions**:
- Update Libby app to latest version
- Logout and back in to Libby app
- Clear kLibby auth: Settings → Clear Authentication

## Code Example

Full authentication flow in kLibby:

```python
from libby.client import LibbyClient
import time

# 1. Initialize client
client = LibbyClient()

# 2. Generate code
response = client.generate_clone_code()
code = response.get('code', '')

print(f"Enter this code in Libby: {code}")

# 3. Wait for user to enter code in Libby app
print("Waiting for authentication...")

# 4. Poll for completion
for attempt in range(30):  # 1 minute
    try:
        sync_data = client.verify_clone_status()

        if sync_data.get('cards'):
            print("Success! Authenticated.")
            break
    except:
        pass  # Not authenticated yet

    time.sleep(2)
else:
    print("Timeout - please try again")

# 5. Use client
loans = client.get_loans()
```

## References

- [Libby Help: Setting up on another device](https://help.libbyapp.com/en-us/6070.htm)
- [libby-calibre-plugin source](https://github.com/ping/libby-calibre-plugin/blob/main/calibre-plugin/libby/client.py)
- [Libby Authentication Changes (2024)](https://techtips.colonielibrary.org/copy-libby/)

## Summary

✅ **What you need to know**:
1. kLibby now **generates** the code
2. You **enter** it in Libby app
3. kLibby **auto-detects** when done
4. Takes ~1 minute max

✅ **What changed in the code**:
- Added `generate_clone_code()` method
- Added `verify_clone_status()` polling
- Updated UI to show generated code
- Auto-polling every 2 seconds

✅ **What to do**:
- Just use kLibby normally
- Follow the on-screen instructions
- The new flow is automatic!
