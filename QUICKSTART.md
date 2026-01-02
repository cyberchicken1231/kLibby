# kLibby Quick Start Guide

Get up and running with kLibby in 5 minutes!

## What You Need

- ✅ Jailbroken Kindle Paperwhite Gen 11
- ✅ Python 3.7+ installed on Kindle
- ✅ WiFi connection
- ✅ Libby account with library card

## Installation (3 Steps)

### 1. Download kLibby

```bash
# On your Kindle (via SSH)
cd /mnt/us
wget https://github.com/cyberchicken1231/kLibby/releases/latest/download/klibby-0.1.0.tar.gz
tar -xzf klibby-0.1.0.tar.gz
cd klibby
```

Or copy via USB:
1. Download release to computer
2. Extract and copy `klibby` folder to Kindle USB drive
3. Eject Kindle

### 2. Install

```bash
cd /mnt/us/klibby
./install.sh
```

### 3. Run

```bash
klibby
# or
./klibby.sh
```

## First Use (2 Steps)

### 1. Connect to Libby

In kLibby menu:
- Select "Connect to Libby"
- kLibby generates an 8-digit code
- Note the code shown on screen

On your phone/tablet (Libby app):
- Settings (⋮) → Copy To Another Device
- Enter the code from kLibby

Back on Kindle:
- Wait for authentication (auto-detects)
- Done! ✨

### 2. Download a Book

- Select "My Loans"
- Choose a book
- Select "Download Book"
- Read with KOReader or convert to MOBI

## Done!

You're all set! 🎉

## Next Steps

- Read [USAGE.md](docs/USAGE.md) for detailed features
- Check [TIPS.md](docs/TIPS.md) for advanced tricks
- Install KOReader for best ePub reading experience

## Quick Commands

```bash
# Launch kLibby
klibby

# Navigate
↑/↓ or J/K  - Move selection
Enter       - Select
B           - Back
Q           - Quit

# Downloads saved to
/mnt/us/kLibby/downloads/
```

## Need Help?

- 📖 Full guide: [INSTALL.md](INSTALL.md)
- 🐛 Issues: https://github.com/cyberchicken1231/kLibby/issues
- 💬 Forums: https://www.mobileread.com/forums/

Enjoy your library books on Kindle! 📚
