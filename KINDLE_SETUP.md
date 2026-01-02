# Quick Kindle Setup Guide

If you're seeing errors on your Kindle, use this guide.

## Common Errors & Fixes

### Error: "setupterm: could not find terminal"

**Fix**: Set TERM variable
```bash
export TERM=linux
```

### Error: "SSL: CERTIFICATE_VERIFY_FAILED"

**Fix**: Kindle has outdated CA certificates. The launcher handles this automatically.

### Error: "HTTP 403: missing_chip"

**Fix**: Authentication flow needs identity token first. Updated in latest version.

## Quick Install on Kindle

```bash
# 1. You're in /mnt/us/kLibby
cd /mnt/us/kLibby

# 2. The launcher is already there - just run it:
./klibby.sh

# That's it! The launcher handles:
# ✓ TERM variable
# ✓ SSL certificates
# ✓ Python path
# ✓ Everything!
```

## What the Launcher Does

The `klibby.sh` script automatically:
1. Sets `TERM=linux` for curses
2. Disables SSL verification (Kindle's certs are outdated)
3. Sets up Python path
4. Launches kLibby

## Manual Run (if launcher doesn't work)

```bash
cd /mnt/us/kLibby/src

TERM=linux python3 << 'EOF'
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import main
main.main()
EOF
```

## First Time Authentication

1. Run kLibby: `./klibby.sh`
2. Select "Connect to Libby"
3. kLibby shows you an 8-digit code
4. Open Libby app on phone
5. Settings → Copy To Another Device
6. Enter the code from kLibby
7. Wait ~10 seconds
8. Done!

## Troubleshooting

### Menu doesn't appear

**Problem**: TERM not set

**Fix**:
```bash
export TERM=linux
./klibby.sh
```

### "missing_chip" error

**Problem**: Outdated version

**Fix**: Pull latest code from git
```bash
cd /mnt/us/kLibby
git pull origin claude/libby-kindle-app-0sQdB
```

### Authentication times out

**Problem**: Network issue or code expired

**Solutions**:
- Check WiFi connection
- Try generating a new code
- Make sure Libby app is up to date

### Can't download books

**Problem**: Need to authenticate first

**Fix**:
1. Settings → Clear Authentication
2. Connect to Libby again
3. Try download

## Files You Need

Minimum required on Kindle:
```
/mnt/us/kLibby/
├── klibby.sh          ← Launcher (run this!)
└── src/
    ├── main.py
    ├── libby/
    │   ├── __init__.py
    │   ├── client.py
    │   └── models.py
    └── ui/
        ├── __init__.py
        └── menu.py
```

## Command Reference

```bash
# Launch kLibby
cd /mnt/us/kLibby
./klibby.sh

# Check if Python works
python3 --version

# Check TERM is set
echo $TERM

# Test imports
cd /mnt/us/kLibby/src
python3 -c "from libby.client import LibbyClient; print('OK')"
```

## Environment Variables

Add these to `~/.profile` for permanent setup:
```bash
export TERM=linux
export PATH="/mnt/us/bin:$PATH"
```

Then reload:
```bash
source ~/.profile
```

## Support

- **Issues**: https://github.com/cyberchicken1231/kLibby/issues
- **Docs**: See README.md and INSTALL.md
- **Forums**: https://www.mobileread.com/forums/

Happy reading! 📚
