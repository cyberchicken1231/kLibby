# kLibby Interface Options

kLibby has two interface options:

## Simple Text Interface (Default)

**File**: `main_simple.py`

Clean numbered menus - perfect for Kindle:

```
============================================================
  kLibby - Libby for Kindle
============================================================

  1. Connect to Libby
  2. About
  3. Quit

------------------------------------------------------------

Enter choice (or 'q' to quit):
```

**Advantages**:
- ✅ Works on all terminals
- ✅ No special keys needed
- ✅ Clear and readable
- ✅ Perfect for e-ink
- ✅ No flickering

**How to use**:
- Type a number and press Enter
- Type `q` to quit
- That's it!

## Curses Interface (Alternative)

**File**: `main.py`

Full-screen curses-based menu with arrow key navigation:

**Advantages**:
- ✅ Prettier visuals
- ✅ Arrow key navigation
- ✅ Highlighted selections

**Disadvantages**:
- ❌ May not work on all Kindle terminals
- ❌ Arrow keys can be finicky
- ❌ Can flicker on some devices

## Switching Interfaces

### Use Simple (Default):
```bash
cd /mnt/us/kLibby/src
python3 << 'EOF'
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import main_simple
main_simple.main()
EOF
```

### Use Curses:
```bash
cd /mnt/us/kLibby/src
export TERM=linux
python3 << 'EOF'
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import main
main.main()
EOF
```

## Launcher Configuration

The `klibby.sh` launcher is configured to use the **simple interface** by default since it works reliably on all Kindle devices.

To permanently switch, edit the launcher:

```bash
# For simple interface (default):
import main_simple
main_simple.main()

# For curses interface:
import main
main.main()
```

## Recommendation

**Use simple interface** (`main_simple.py`) for:
- Kindle terminals
- SSH sessions
- Reliability
- Simplicity

**Use curses interface** (`main.py`) for:
- Desktop testing
- Better terminal support
- Visual preference

Happy reading! 📚
