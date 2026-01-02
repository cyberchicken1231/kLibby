# kLibby - Libby Client for Jailbroken Kindle

A lightweight Libby (OverDrive) client designed specifically for jailbroken Kindle Paperwhite devices.

## Overview

kLibby allows you to browse, checkout, and read library books from Libby/OverDrive directly on your jailbroken Kindle Paperwhite. Built for e-ink displays and optimized for the Kindle's limited resources.

## Target Device

- **Kindle Paperwhite Gen 11** (5th generation Paperwhite)
- **CPU**: ARMv7 32-bit hardfloat
- **Jailbreak**: AdBreak or compatible
- **Display**: E-ink optimized UI

## Features

- 📚 Browse your Libby library
- 🔍 Search for books
- ✅ Checkout and borrow books
- 📖 Download books in ePub/PDF format
- 🔄 Manage loans and holds
- 📱 Sync with your Libby account via 8-digit code

## Architecture

kLibby is built using:
- **Python 3.10+** (3.11+ recommended) - Core application logic with modern type hints
- **Libby API** - Based on reverse-engineered endpoints from odmpy
- **E-ink UI** - Lightweight interface optimized for Kindle display
- **Cross-compiled** - Built for ARMv7 hardfloat architecture

## API Information

Based on research from existing projects:
- Main API: `https://sentry-read.svc.overdrive.com/`
- Authentication: Bearer token via identity chip
- Sync code: 8-digit code from Libby app for device linking

### Key References:
- [odmpy](https://github.com/ping/odmpy) - Command-line OverDrive/Libby manager
- [libby-calibre-plugin](https://github.com/ping/libby-calibre-plugin) - Calibre plugin with Libby client
- [OverDrive Developer Portal](https://developer.overdrive.com/)

## Project Structure

```
kLibby/
├── src/
│   ├── libby/          # Libby API client
│   ├── ui/             # E-ink optimized UI
│   ├── utils/          # Helper utilities
│   └── main.py         # Main application entry
├── build/              # Build scripts for ARMv7
├── docs/               # Documentation
├── tests/              # Test suite
└── README.md
```

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions for jailbroken Kindle devices.

## Usage

1. Launch kLibby from your Kindle
2. kLibby generates an 8-digit code and displays it
3. Open Libby app on phone: Settings → Copy to another device → Enter the code
4. Browse and checkout books
5. Read directly or convert to Kindle format

## Development Status

🚧 **In Development** - This project is currently being built.

## Legal & Disclaimer

This project is:
- **Not affiliated** with OverDrive, Inc. or Libby
- For **personal use** only with valid library credentials
- Respects library lending rules and DRM where applicable
- Educational/research purposes

You must have a valid library card and Libby account to use this software.

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Please see CONTRIBUTING.md

## Acknowledgments

- [odmpy](https://github.com/ping/odmpy) by ping - Python Libby API implementation
- [libby-calibre-plugin](https://github.com/ping/libby-calibre-plugin) - API reference
- MobileRead Forums - Kindle development community
