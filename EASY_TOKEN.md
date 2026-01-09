# Easy Token Extraction

The simplest way to get your Libby authentication token - **you do the clicking, we capture the token!**

## How It Works

1. Script opens a browser window
2. **You** manually log into Libby (just like you normally would)
3. **You** click on any book
4. Script automatically captures the Authorization token
5. Token gets saved to kLibby

**No automation headaches. No complicated setup. Just click and go.**

## Quick Start

```bash
cd ~/kLibby
python3 easy_token.py
```

That's it! The script will:
- Open Chrome to libbyapp.com
- Wait for you to sign in
- Automatically detect and save your token when you click a book

## Step by Step

### 1. Run the script

```bash
python3 easy_token.py
```

### 2. In the browser window that opens:

- Search for your library
- Click "Sign In with library card"
- Enter your card number and PIN
- **Click on any book in your shelf**

### 3. Done!

The script will automatically:
- Capture the Authorization header
- Show you the token expiration date
- Save it to `~/.klibby/settings.json`

You'll see:
```
✓ FOUND IT! Token captured (length: 611)
✅ SUCCESS! Token saved to kLibby!
```

## Requirements

Just Selenium:

```bash
pip install selenium --break-system-packages
```

## Why This Is Better

**Old way (auto_refresh_token.py):**
- ❌ Store credentials in plain text
- ❌ Fragile element selectors
- ❌ Breaks when Libby UI changes
- ❌ Element interaction issues

**New way (easy_token.py):**
- ✅ No credentials storage needed
- ✅ You control the login (no automation)
- ✅ Works even if Libby UI changes
- ✅ No interaction issues
- ✅ Super simple!

## Troubleshooting

**"No token found after 5 minutes"**

Make sure you clicked on a book! The token is only sent when you interact with content.

**"Module 'selenium' not found"**

```bash
pip install selenium --break-system-packages
```

**"chromedriver not found"**

```bash
sudo snap install chromium
# or
sudo apt install chromium chromium-driver
```

## Token Expires in 7 Days

When your token expires, just run `easy_token.py` again. Takes 30 seconds!

Want automatic renewal? Use `auto_refresh_token.py` instead (more complex setup).

## Security

- No credentials stored anywhere
- Token saved to `~/.klibby/settings.json` (same as manual method)
- Only readable by your user account
- Network traffic monitoring is local (nothing sent anywhere)
