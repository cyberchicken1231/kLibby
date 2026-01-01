# kLibby Usage Guide

Detailed guide for using kLibby on your Kindle.

## Getting Started

### First Launch

1. **Start kLibby**:
   ```bash
   klibby  # If in PATH
   # or
   cd /mnt/us/klibby && ./klibby.sh
   ```

2. **You'll see the main menu**:
   ```
   ==================================================
                      kLibby - Libby for Kindle
   ==================================================

   > Connect to Libby
     About
     Quit

   --------------------------------------------------
   ↑/↓: Navigate | Enter: Select | Q: Quit
   ```

### Connecting to Libby

1. **Select "Connect to Libby"** from the main menu

2. **Read the instructions**:
   - Open Libby app on your phone/tablet
   - Go to Settings (three dots menu)
   - Select "Copy To Another Device"
   - Note the 8-digit code displayed

3. **Enter the sync code** when prompted

4. **Success!** Your Kindle is now linked to your Libby account

## Main Features

### My Loans

View and manage your currently checked out books.

**To view loans**:
1. Select "My Loans" from main menu
2. Browse your active loans
3. See expiration dates for each book

**To download a book**:
1. Select the book from "My Loans"
2. Choose "Download Book"
3. Book is saved to `/mnt/us/kLibby/downloads/`
4. Files are in ePub format (or .acsm if DRM-protected)

**To return a book early**:
1. Select the book from "My Loans"
2. Choose "Return Early"
3. Confirm the return

### My Holds

View books you have on hold.

1. Select "My Holds" from main menu
2. See all your holds and their status
3. "Available!" means ready to borrow
4. "Waiting" means still in queue

### Library Cards

View all library cards linked to your Libby account.

1. Select "Library Cards" from main menu
2. See all your library systems
3. View usernames associated with each card

## Reading Downloaded Books

kLibby downloads books in ePub format. To read them on your Kindle:

### Option 1: KOReader (Recommended)

1. **Install KOReader**:
   - Download from https://koreader.rocks/
   - Install as KUAL extension
   - Launch from KUAL menu

2. **Open your book**:
   - Launch KOReader
   - Navigate to `/mnt/us/kLibby/downloads/`
   - Select and open your ePub file

### Option 2: Convert to Kindle Format

1. **Use Calibre on your computer**:
   - Download Calibre: https://calibre-ebook.com/
   - Connect Kindle via USB
   - Add ePub book to Calibre
   - Convert to MOBI or AZW3
   - Send to Kindle

2. **Via email** (if Kindle has email):
   - Email ePub to your Kindle email address
   - Amazon will convert it automatically

### Option 3: Native Kindle Reader

Some newer Kindles support ePub natively:
- Check if your Kindle firmware supports ePub
- If yes, books appear in your library automatically

## Keyboard Controls

### Navigation

- **↑/K**: Move selection up
- **↓/J**: Move selection down
- **Enter**: Select current item
- **B**: Go back to previous menu
- **Q**: Quit application

### In Lists

- **↑/↓**: Scroll through items
- **Enter**: Select item
- **B**: Back to main menu

### Text Input

- **Type normally**: Enter text
- **Backspace**: Delete characters
- **Enter**: Submit input
- **Ctrl+C**: Cancel input

## Tips & Tricks

### Quick Access

Create a shell alias for faster launching:
```bash
# Add to ~/.bashrc or ~/.profile
alias libby='cd /mnt/us/klibby && ./klibby.sh'
```

Then just type `libby` to launch!

### Auto-Download

To automatically download all available holds, you could create a script:
```bash
#!/bin/sh
# auto-download.sh
# (Feature to be added in future version)
```

### Batch Operations

Currently kLibby handles one book at a time. For batch operations, use the Libby app on your phone.

## Download Formats

### ePub (Open Format)

- **Best choice** for Kindle reading
- No DRM restrictions
- Compatible with KOReader
- Can be converted easily

### ACSM (Adobe DRM)

- DRM-protected format
- Requires Adobe Digital Editions to open
- Cannot be read directly on Kindle
- Workaround: Open on computer with ADE, then transfer

**To handle ACSM files**:
1. Download on Kindle
2. Transfer to computer via USB
3. Open with Adobe Digital Editions
4. Book downloads as ePub
5. Transfer back to Kindle or convert to MOBI

## Settings

### Clear Authentication

To logout from Libby:
1. Select "Settings" from main menu
2. Choose "Clear Authentication"
3. Your sync data is removed
4. You'll need to re-authenticate next time

### Download Location

Downloads are saved to:
```
/mnt/us/kLibby/downloads/
```

Files are named after the book title.

### Configuration File

Settings are stored in:
```
~/.klibby/settings.json
```

Contains:
- Identity token (for authentication)
- Custom settings (if any)

**DO NOT share your settings.json** - it contains your authentication token!

## Troubleshooting

### "No loans found"

- Check if you have any books checked out in Libby app
- Try refreshing by going back to main menu and re-entering

### "Download failed"

- Check available storage space
- Verify internet connection
- Ensure loan hasn't expired
- Try re-downloading

### "Authentication expired"

- Your session may have timed out
- Go to Settings → Clear Authentication
- Re-authenticate with new sync code

### Can't see books in Kindle library

- kLibby downloads to custom location
- Use KOReader or file browser to access
- Or convert and send via Calibre

## Advanced Usage

### SSH Remote Control

You can manage kLibby remotely via SSH:

```bash
# From your computer
ssh root@kindle
cd /mnt/us/klibby
./klibby.sh
```

Use with tmux/screen for background sessions:
```bash
ssh root@kindle
tmux
./klibby.sh
# Detach: Ctrl+B, D
# Reattach: tmux attach
```

### Scripting

kLibby is Python-based, so you can script it:

```python
#!/usr/bin/env python3
from libby.client import LibbyClient

client = LibbyClient()
loans = client.get_loans()

for loan in loans:
    print(f"Title: {loan.title.title}")
    print(f"Expires: {loan.expire_date}")
```

### Custom UI

The curses UI can be modified in `src/ui/menu.py`:
- Change colors
- Adjust layout
- Customize key bindings

## Known Limitations

1. **Search/Browse** - Currently not implemented
   - Use Libby app to search and checkout
   - kLibby manages existing loans

2. **Audiobooks** - Not yet supported
   - ePub/PDF books only for now
   - Audiobook support planned for future

3. **Reading Interface** - kLibby downloads only
   - Use KOReader or Kindle's native reader
   - Integrated reader may come in future version

4. **Magazines** - Limited support
   - Downloads work
   - May need specific reader for best experience

## Getting Help

- **GitHub Issues**: https://github.com/cyberchicken1231/kLibby/issues
- **Documentation**: Check `/docs` folder
- **MobileRead**: Search or ask in Kindle forums

## Next Steps

- **Explore**: Try all the features!
- **Customize**: Modify settings to your liking
- **Contribute**: Found a bug? Submit an issue!
- **Share**: Help others discover kLibby

Happy reading! 📖
