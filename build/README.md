# Building kLibby for Kindle

## Overview

kLibby is a pure Python application, so it doesn't require compilation. However, you need to ensure Python is available on your Kindle and package the application for easy deployment.

## Prerequisites

### On Your Development Machine:
- Python 3.7+ installed
- Git (for cloning the repository)

### On Your Kindle:
- Kindle Paperwhite Gen 11 (5th gen Paperwhite)
- Jailbroken with AdBreak or compatible jailbreak
- Python 3.x installed (see installation guide)
- SSH access enabled (recommended)

## Building for Kindle

Since kLibby uses only Python standard library, building is straightforward:

### Method 1: Direct Deployment (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/cyberchicken1231/kLibby.git
   cd kLibby
   ```

2. Create a deployment package:
   ```bash
   ./build/package.sh
   ```

   This creates `klibby.tar.gz` containing all necessary files.

3. Transfer to Kindle:
   ```bash
   scp klibby.tar.gz root@kindle:/mnt/us/
   ```

4. On Kindle, extract and install:
   ```bash
   ssh root@kindle
   cd /mnt/us
   tar -xzf klibby.tar.gz
   cd klibby
   python3 src/main.py
   ```

### Method 2: Using Setup.py

1. Build distribution package:
   ```bash
   python3 setup.py sdist
   ```

2. Transfer to Kindle and install:
   ```bash
   scp dist/klibby-0.1.0.tar.gz root@kindle:/mnt/us/
   ssh root@kindle
   cd /mnt/us
   tar -xzf klibby-0.1.0.tar.gz
   cd klibby-0.1.0
   python3 setup.py install --user
   ```

## Python on Kindle

If Python is not installed on your Kindle:

### Installing Python via KUAL

1. Download Python package for Kindle from MobileRead
2. Install via KUAL (Kindle Unified Application Launcher)
3. Verify: `python3 --version`

### Installing Python Manually

See INSTALL.md for detailed instructions on installing Python on your specific Kindle model.

## Testing on Desktop

Before deploying to Kindle, test on your desktop:

```bash
cd kLibby
python3 src/main.py
```

This will run kLibby in a terminal window using curses.

## Troubleshooting

### "ModuleNotFoundError" on Kindle
- Ensure Python 3.7+ is installed
- Verify PYTHONPATH includes the src directory

### "Terminal too small" error
- The Kindle terminal needs at least 24 rows × 80 columns
- This should work by default on SSH sessions

### Curses not working
- Ensure TERM environment variable is set: `export TERM=xterm`
- On Kindle: `export TERM=linux`

## Cross-Compilation Notes

kLibby doesn't require cross-compilation since it's pure Python. However, if you need to bundle Python itself:

- **Architecture**: ARMv7 32-bit hardfloat (armhf)
- **Python Version**: 3.7+ recommended
- **OS**: Linux-based Kindle OS

## Creating a KUAL Extension

For easier launching from Kindle UI:

1. Create KUAL extension structure (see `build/kual/`)
2. Place launcher script in menu
3. Install in `/mnt/us/extensions/klibby/`

See `build/create_kual_extension.sh` for automated creation.
