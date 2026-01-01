# kLibby Tips & Tricks

Advanced tips and tricks for getting the most out of kLibby on your Kindle.

## E-ink Display Optimization

### Reduce Screen Refreshes

E-ink displays are slow to refresh. To minimize refreshes:

1. **Navigate efficiently**: Use J/K keys instead of arrows (fewer refreshes)
2. **Plan your path**: Know what you want before diving into menus
3. **Use partial refresh** (if your Kindle supports it)

### Best Reading Experience

For the best reading experience with downloaded books:

1. **Use KOReader**:
   - Superior ePub support
   - Partial screen refresh
   - Better font rendering
   - Dictionary support

2. **Adjust lighting**:
   - Turn off auto-brightness
   - Use warm light mode for night reading

## Workflow Optimization

### Efficient Book Management

**On the go workflow**:
1. Browse and checkout books using Libby app on phone
2. Open kLibby on Kindle
3. View new loans
4. Download and read immediately

**Batch download workflow**:
1. Checkout multiple books in Libby app during the week
2. Weekend: Download all via kLibby
3. Read throughout the week

### Library Card Management

**Multiple libraries**:
- Link cards from multiple library systems
- Each library has different selections
- kLibby shows all loans from all cards

**Maximizing checkouts**:
- Most libraries allow 10+ simultaneous checkouts
- Use all your slots for variety
- Return early if you finish quickly (helps others!)

## Power User Features

### Shell Aliases

Add to `~/.profile` on Kindle:

```bash
# Quick launch
alias kl='cd /mnt/us/klibby && ./klibby.sh'

# View loans without launching UI
alias loans='python3 /mnt/us/klibby/src/list_loans.py'

# Quick download
alias dl='python3 /mnt/us/klibby/src/download.py'
```

### Keyboard Shortcuts

Create a script for one-touch download:

```bash
#!/bin/sh
# quick-download.sh
# Downloads first available loan

cd /mnt/us/klibby
python3 << 'EOF'
from libby.client import LibbyClient

client = LibbyClient()
loans = client.get_loans()

if loans:
    first_loan = loans[0]
    print(f"Downloading: {first_loan.title.title}")
    client.download_book(
        first_loan.card_id,
        first_loan.loan_id,
        f"/mnt/us/kLibby/downloads/{first_loan.title.title}.epub"
    )
    print("Done!")
else:
    print("No loans found")
EOF
```

### Automated Downloads

Use cron (if available on your Kindle) for automatic downloads:

```bash
# Add to crontab
# Download new loans every day at 3 AM
0 3 * * * /mnt/us/klibby/auto-download.sh
```

## Reading Tips

### Best Formats for Kindle

1. **ePub (Open)** ← Best choice
   - No DRM
   - Works with KOReader
   - Easy to convert

2. **PDF** (if no ePub available)
   - Fixed layout
   - May require zooming
   - Better on larger Kindle models

3. **MOBI/AZW3** (after conversion)
   - Native Kindle format
   - Best integration
   - Requires conversion step

### Handling DRM Books

If you checkout a DRM-protected book (.acsm):

**Method 1: Read on computer/tablet**
- Transfer .acsm to computer
- Open with Adobe Digital Editions
- Read there instead

**Method 2: DRM removal** (legal for personal use)
- Use Calibre with DeDRM plugin
- Open .acsm in Adobe Digital Editions first
- Import to Calibre to strip DRM
- **Note**: Only for personal use, don't share!

### Organization

Create folders for different genres:

```bash
mkdir -p /mnt/us/kLibby/downloads/{fiction,non-fiction,technical,magazines}
```

Modify download path based on book type.

## Network Tips

### Optimize for Slow Connections

If you have slow WiFi:

1. **Download during off-peak hours**
2. **Use Kindle's WiFi instead of hotspot**
3. **Download smaller files first** (PDFs usually smaller than ePubs)

### Offline Reading

1. Download books when you have WiFi
2. Turn off WiFi to save battery
3. Read offline with KOReader
4. Re-enable WiFi only for new downloads

## Battery Optimization

### Extend Battery Life

1. **Turn off WiFi** when not downloading
2. **Close kLibby** when not in use (don't leave running)
3. **Use airplane mode** for pure reading
4. **Reduce screen brightness**

### Quick Launch Setup

Instead of keeping kLibby running:
- Create KUAL shortcut for one-tap launch
- Launch, download, quit
- Save battery vs. keeping app open

## Kindle Hacks Integration

### Works Great With:

1. **KOReader** - Best ePub reader for Kindle
2. **Plato** - Alternative reader
3. **KUAL** - Launch kLibby from menu
4. **USBNetwork** - SSH access for remote management
5. **Calibre** - Organize and convert books

### Create a Reading Workflow

1. **Browse** on phone via Libby (during commute)
2. **Checkout** interesting books
3. **Download** via kLibby when home
4. **Convert** with Calibre if needed
5. **Read** with KOReader on Kindle

## Advanced Authentication

### Multiple Devices

You can use the same Libby account on:
- Your phone (Libby app)
- Your tablet (Libby app)
- Your Kindle (kLibby)
- Your computer (Libby web)

All synced via your library account!

### Re-authentication

If your token expires:
```bash
# Quick re-auth
cd /mnt/us/klibby
rm ~/.klibby/settings.json
./klibby.sh
# Follow setup wizard again
```

## Scripting Examples

### List All Loans

```python
#!/usr/bin/env python3
# list_loans.py

from libby.client import LibbyClient

client = LibbyClient()
loans = client.get_loans()

print(f"\nYou have {len(loans)} loan(s):\n")

for i, loan in enumerate(loans, 1):
    title = loan.title.title
    authors = ", ".join(loan.title.authors) if loan.title.authors else "Unknown"
    expires = loan.expire_date.strftime("%Y-%m-%d") if loan.expire_date else "Unknown"

    print(f"{i}. {title}")
    print(f"   By: {authors}")
    print(f"   Expires: {expires}\n")
```

### Auto-Return Expired Loans

```python
#!/usr/bin/env python3
# return_expired.py

from libby.client import LibbyClient
from datetime import datetime

client = LibbyClient()
loans = client.get_loans()

now = datetime.now()

for loan in loans:
    if loan.expire_date and loan.expire_date < now:
        print(f"Returning expired: {loan.title.title}")
        client.return_loan(loan.card_id, loan.loan_id)
```

## Troubleshooting Tips

### Debug Mode

Enable verbose logging:

```bash
# Set debug env var
export KLIBBY_DEBUG=1
./klibby.sh
```

### Network Issues

Test connectivity:
```bash
# On Kindle
ping 8.8.8.8  # Test internet
ping sentry-read.svc.overdrive.com  # Test Libby API

# If DNS fails but ping works, check /etc/resolv.conf
```

### Storage Management

Check available space:
```bash
df -h /mnt/us
```

Clean old downloads:
```bash
# Remove books older than 30 days
find /mnt/us/kLibby/downloads -name "*.epub" -mtime +30 -delete
```

## Community Tips

### Share Your Workflows

Found a great workflow? Share it on:
- MobileRead forums
- GitHub discussions
- Reddit r/kindle

### Contribute Back

Help improve kLibby:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## Future Enhancements

Features you can help implement:

1. **Search/Browse** - Search library catalog from Kindle
2. **Audiobook support** - Download and play audiobooks
3. **Reading stats** - Track reading time and progress
4. **Series detection** - Group books by series
5. **Recommendation engine** - Suggest books based on history

## Final Tips

1. **Start simple** - Learn basic features first
2. **Experiment** - kLibby won't break your Kindle
3. **Backup** - Keep a copy of your settings
4. **Be patient** - E-ink is slow but worth it!
5. **Have fun** - Enjoy unlimited library books on your Kindle!

## Resources

- **MobileRead**: https://www.mobileread.com/forums/
- **KOReader**: https://koreader.rocks/
- **Calibre**: https://calibre-ebook.com/
- **Libby Help**: https://help.libbyapp.com/

Happy hacking! 🚀📚
