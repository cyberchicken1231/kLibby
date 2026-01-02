# kLibby Installation Guide

Complete installation guide for kLibby on jailbroken Kindle devices.

## Prerequisites

### Kindle Requirements

- **Device**: Kindle Paperwhite Gen 11 (5th generation Paperwhite)
- **Firmware**: Any version compatible with jailbreak
- **Jailbreak**: AdBreak or compatible jailbreak installed
- **Storage**: At least 50MB free space

### What You'll Need

1. Jailbroken Kindle Paperwhite
2. USB cable for data transfer
3. Computer (Windows, Mac, or Linux)
4. Libby account with library card(s)
5. Basic familiarity with terminal/command line (helpful but not required)

## Quick Start (For Experienced Users)

```bash
# 1. Download and transfer to Kindle
wget https://github.com/cyberchicken1231/kLibby/releases/latest/download/klibby-0.1.0.tar.gz
# Copy to Kindle via USB or scp

# 2. On Kindle (via SSH)
cd /mnt/us
tar -xzf klibby-0.1.0.tar.gz
cd klibby
./install.sh

# 3. Run kLibby
klibby
```

## Detailed Installation Steps

### Step 1: Jailbreak Your Kindle

If your Kindle is not already jailbroken:

1. **Check your firmware version**:
   - Go to Settings → Device Info on your Kindle
   - Note the firmware version

2. **Jailbreak with AdBreak**:
   - Visit MobileRead Forums: https://www.mobileread.com/forums/
   - Search for "Kindle Paperwhite 11 jailbreak"
   - Follow the AdBreak installation guide for your firmware version
   - **IMPORTANT**: Read the guide carefully before proceeding

3. **Install KUAL** (Kindle Unified Application Launcher):
   - Download KUAL from MobileRead
   - Extract to `/mnt/us/` on your Kindle
   - This provides a menu for launching applications

### Step 2: Install Python on Kindle

kLibby requires Python 3.10 or later (Python 3.11+ recommended). Several methods are available:

#### Method A: Python via KUAL Extension (Easiest)

1. Download Python KUAL extension from MobileRead
2. Connect Kindle to computer via USB
3. Copy the extension to `/extensions/` folder
4. Eject Kindle safely
5. Launch KUAL and install Python

#### Method B: Manual Python Installation

1. Download Python 3.11+ for ARM (armhf):
   ```bash
   # On your computer
   wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
   ```

2. Cross-compile for ARMv7 or download pre-built binaries from:
   - https://github.com/NiLuJe/kindletool
   - MobileRead Python packages

3. Transfer to Kindle and extract to `/mnt/us/python/`

4. Add to PATH (create `/etc/profile.d/python.sh`):
   ```bash
   export PATH="/mnt/us/python/bin:$PATH"
   ```

#### Method C: Use Entware (Advanced)

Entware is a package manager for embedded devices:

1. Install Entware on Kindle (see Entware-ng for Kindle guide)
2. Install Python via opkg:
   ```bash
   opkg update
   opkg install python3
   ```

### Step 3: Enable SSH Access (Recommended)

SSH makes installation and management much easier:

1. **Install USBNetwork** (from MobileRead):
   - Download USBNetwork package
   - Extract to Kindle
   - Enable via KUAL menu

2. **Connect to Kindle**:
   ```bash
   # From your computer
   ssh root@192.168.15.244  # Default USBNetwork IP
   # or
   ssh root@kindle.local
   ```

   Default password is usually blank or set during USBNetwork setup.

### Step 4: Install kLibby

#### Via SSH (Recommended)

1. **Download kLibby package**:
   ```bash
   # On Kindle via SSH
   cd /mnt/us
   wget https://github.com/cyberchicken1231/kLibby/releases/latest/download/klibby-0.1.0.tar.gz
   ```

   Or transfer manually via USB.

2. **Extract package**:
   ```bash
   tar -xzf klibby-0.1.0.tar.gz
   cd klibby
   ```

3. **Run installation script**:
   ```bash
   ./install.sh
   ```

   This will:
   - Check for Python
   - Copy files to `/mnt/us/klibby/`
   - Create launcher script
   - Set up PATH if possible

#### Via USB (Manual Installation)

1. **Connect Kindle to computer** via USB

2. **Copy kLibby**:
   - Extract `klibby-0.1.0.tar.gz` on your computer
   - Copy the entire `klibby` folder to your Kindle's USB drive
   - Eject Kindle safely

3. **On Kindle** (via SSH or terminal):
   ```bash
   cd /mnt/us/klibby
   chmod +x klibby.sh
   chmod +x install.sh
   ./install.sh
   ```

### Step 5: First Run

1. **Launch kLibby**:
   ```bash
   cd /mnt/us/klibby
   ./klibby.sh
   ```

   Or if installed to PATH:
   ```bash
   klibby
   ```

2. **Set up Libby authentication**:
   - On first run, select "Connect to Libby"
   - kLibby generates and displays an 8-digit code
   - On your phone/tablet, open the Libby app
   - Go to Settings (⋮) → Copy To Another Device
   - Enter the code shown on your Kindle
   - kLibby automatically detects when authentication completes

3. **Browse and checkout books**!

## Creating a KUAL Menu Entry (Optional)

To launch kLibby from the KUAL menu:

1. **Create KUAL extension structure**:
   ```bash
   mkdir -p /mnt/us/extensions/klibby
   ```

2. **Create menu file** (`/mnt/us/extensions/klibby/menu.json`):
   ```json
   {
     "items": [
       {
         "name": "Launch kLibby",
         "priority": 1,
         "action": "/mnt/us/klibby/klibby.sh",
         "exitmenu": true
       }
     ]
   }
   ```

3. **Restart KUAL** - kLibby should now appear in the menu

## Usage

### Basic Navigation

- **↑/↓ or J/K**: Navigate menu items
- **Enter**: Select item
- **B**: Go back
- **Q**: Quit application

### Common Tasks

**View Your Loans**:
1. Launch kLibby
2. Select "My Loans"
3. Choose a book to download or return

**Download a Book**:
1. Go to "My Loans"
2. Select the book
3. Choose "Download Book"
4. Book saved to `/mnt/us/kLibby/downloads/`

**Return a Book Early**:
1. Go to "My Loans"
2. Select the book
3. Choose "Return Early"

## Troubleshooting

### Python Not Found

**Error**: `python3: command not found`

**Solution**:
- Verify Python installation: `which python3`
- Check PATH: `echo $PATH`
- Manually specify Python path in `klibby.sh`

### Terminal Issues

**Error**: `Terminal too small` or curses errors

**Solution**:
```bash
export TERM=linux  # On Kindle
# or
export TERM=xterm  # If using SSH
```

### Network/SSL Errors

**Error**: SSL certificate errors when connecting to Libby

**Solution**:
- Ensure Kindle's date/time is correct
- Update ca-certificates package if available
- Check internet connectivity

### Authentication Failed

**Error**: Can't connect to Libby account

**Solution**:
- Verify the 8-digit sync code is correct
- Make sure code hasn't expired (they expire after a few minutes)
- Generate a new code in Libby app
- Check internet connection

### Books Won't Download

**Error**: Download fails or times out

**Solution**:
- Check available storage space
- Verify loan is still active (not expired)
- Try downloading via WiFi instead of cellular hotspot
- Some books may be DRM-protected (will download as .acsm)

## Advanced Configuration

### Custom Download Location

Edit `~/.klibby/settings.json` to change download path:
```json
{
  "identity_token": "...",
  "download_path": "/mnt/us/documents/libby/"
}
```

### Running at Startup

To launch kLibby automatically on Kindle boot:

1. Create startup script in `/etc/init.d/klibby`:
   ```bash
   #!/bin/sh
   /mnt/us/klibby/klibby.sh &
   ```

2. Make executable: `chmod +x /etc/init.d/klibby`

## Uninstallation

To remove kLibby:

```bash
# Remove application files
rm -rf /mnt/us/klibby

# Remove settings
rm -rf ~/.klibby

# Remove KUAL extension (if installed)
rm -rf /mnt/us/extensions/klibby

# Remove symlink (if created)
rm -f /mnt/us/bin/klibby
```

## Getting Help

- **Issues**: https://github.com/cyberchicken1231/kLibby/issues
- **MobileRead Forums**: https://www.mobileread.com/forums/
- **Kindle Hacking Wiki**: https://wiki.mobileread.com/wiki/Kindle_Hacking

## Legal Notice

kLibby is not affiliated with OverDrive, Inc. or Libby. This software is for personal use only with valid library credentials. Users must comply with their library's terms of service and lending policies.

## Next Steps

After installation, see:
- **README.md** - Project overview and features
- **docs/USAGE.md** - Detailed usage guide
- **docs/TIPS.md** - Tips and tricks for Kindle reading

Happy reading! 📚
