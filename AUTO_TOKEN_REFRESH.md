# Automated Token Refresh

Never manually extract tokens again! This script automatically logs into libbyapp.com and refreshes your authentication token.

## Quick Start

### 1. Install Selenium

```bash
pip install selenium --break-system-packages
```

**Note:** You typed "selinum" but it's actually "selenium" (with an 'e')

### 2. Install Chrome/Chromium

Selenium needs Chrome to work:

```bash
# Debian/Ubuntu
sudo apt install chromium-browser chromium-chromedriver

# Or install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### 3. Save Your Library Credentials

```bash
cd /home/user/kLibby
python3 src/auto_refresh_token.py --setup
```

It will ask for:
- Library card number
- Library card PIN

**⚠ WARNING:** Credentials are stored in **plain text** at `~/.klibby/credentials.json`

### 4. Refresh Token

```bash
python3 src/auto_refresh_token.py
```

This will:
1. Open a headless browser
2. Login to libbyapp.com
3. Capture the Authorization token
4. Save it to kLibby

Done! Your token is refreshed.

## Automation

### Set Up Cron Job (Auto-refresh every 3 days)

```bash
crontab -e
```

Add this line:

```cron
0 3 */3 * * /usr/bin/python3 /home/user/kLibby/src/auto_refresh_token.py
```

This runs every 3 days at 3:00 AM, keeping your token fresh forever.

## Troubleshooting

### "Could not extract Authorization token"

Run with visible browser to see what's happening:

```bash
python3 src/auto_refresh_token.py --no-headless
```

This opens a visible browser window so you can see if:
- Login failed (wrong credentials)
- Libby's interface changed
- CAPTCHA is blocking automation

### "chromedriver not found"

Install ChromeDriver:

```bash
sudo apt install chromium-chromedriver
```

### "Wrong credentials"

Re-run setup:

```bash
python3 src/auto_refresh_token.py --setup
```

## Security

**Plain Text Storage:**
- Credentials stored in `~/.klibby/credentials.json`
- Not encrypted (you chose Option B)
- Only readable by your user account
- Never transmitted anywhere except libbyapp.com

**To delete credentials:**

```bash
rm ~/.klibby/credentials.json
```

## How It Works

1. **Selenium** launches Chrome in headless mode
2. Navigates to https://libbyapp.com
3. Fills in card number and PIN
4. Clicks "Sign In"
5. Monitors network requests for Authorization header
6. Extracts the Bearer token
7. Saves to `~/.klibby/settings.json`

## Manual Extraction Still Needed?

Nope! Once you set this up, you never need to manually extract tokens again. The script does it all automatically.

If you want to check token status:

```bash
python3 -c "
import sys, json, time, base64
sys.path.insert(0, 'src')
from libby.client import LibbyClient
client = LibbyClient()
if not client.identity_token:
    print('No token found')
else:
    parts = client.identity_token.split('.')
    payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
    data = json.loads(base64.b64decode(payload))
    exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['exp']))
    print(f'Token expires: {exp}')
"
```
