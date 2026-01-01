# Python 3.11 Compatibility Notes

## Why Python 3.11?

kLibby is designed to work with Python 3.10+ but is optimized for Python 3.11 and later. Here's why:

### Modern Type Hints (PEP 604, PEP 585)

Python 3.10+ introduced cleaner type hint syntax:

**Old style (Python 3.7-3.9):**
```python
from typing import List, Dict, Optional

def get_loans(self) -> List[Loan]:
    ...

def get_data(self) -> Optional[Dict[str, Any]]:
    ...
```

**New style (Python 3.10+):**
```python
def get_loans(self) -> list[Loan]:
    ...

def get_data(self) -> dict[str, Any] | None:
    ...
```

### Benefits

1. **Cleaner syntax** - No need to import `List`, `Dict`, `Optional` from typing
2. **Better readability** - `str | None` is clearer than `Optional[str]`
3. **Built-in types** - Use `list`, `dict`, `tuple` directly as generics
4. **Future-proof** - Following Python's modern best practices

### Compatibility

The code uses `from __future__ import annotations` which enables:
- Forward references without quotes
- Better compatibility with static type checkers
- Deferred evaluation of annotations

### Python Version Requirements

- **Minimum**: Python 3.10 (for PEP 604 union syntax `X | Y`)
- **Recommended**: Python 3.11+ (performance improvements, better error messages)
- **Tested on**: Python 3.11.9

## Installing Python 3.11 on Kindle

### Option 1: Pre-compiled Binary

Download pre-compiled Python 3.11 for ARMv7:
```bash
# Check MobileRead forums for Kindle Python 3.11 packages
# Or compile yourself (see Option 2)
```

### Option 2: Cross-compile for Kindle

```bash
# On a Linux machine with ARM cross-compiler
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar -xzf Python-3.11.9.tgz
cd Python-3.11.9

# Configure for ARM
./configure \
    --host=arm-linux-gnueabihf \
    --build=x86_64-linux-gnu \
    --prefix=/mnt/us/python \
    --enable-optimizations \
    --with-lto

make -j4
make install DESTDIR=/tmp/python-kindle

# Transfer /tmp/python-kindle/mnt/us/python to your Kindle
```

### Option 3: Use Entware

If you have Entware installed on your Kindle:
```bash
opkg update
opkg install python3
python3 --version  # Should be 3.11+
```

## Verifying Python Version

On your Kindle:
```bash
python3 --version
# Should output: Python 3.11.x or higher

# Test modern syntax support
python3 -c "from __future__ import annotations; x: list[str] = ['test']; print('OK')"
```

## Performance Improvements in Python 3.11

Python 3.11 is **10-60% faster** than Python 3.10:
- Faster startup time
- Optimized frame handling
- Better memory efficiency
- Improved error messages

Perfect for a resource-constrained device like Kindle!

## Type Checking

For development, use mypy to verify type hints:

```bash
pip install mypy
mypy src/
```

Configuration in `setup.cfg`:
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
```

## Migration from Python 3.7-3.9

If you're upgrading from an older Python version:

1. **Update Python**: Install Python 3.11
2. **No code changes needed**: The code uses `from __future__ import annotations`
3. **Enjoy better performance**: Python 3.11 is significantly faster

## Troubleshooting

### "SyntaxError: invalid syntax" on `|` operator

**Problem**: Using Python < 3.10

**Solution**:
- Update to Python 3.10+, or
- Remove `from __future__ import annotations` and use old-style type hints

### Type checker complains about built-in generics

**Problem**: mypy or other type checker version issue

**Solution**:
```bash
pip install --upgrade mypy
```

## Future Plans

- **Python 3.12+**: When available for Kindle, will update
- **Pattern matching**: May add structural pattern matching (PEP 634) in future
- **Performance**: Continue leveraging newer Python optimizations

## References

- [PEP 604 - Union Types](https://peps.python.org/pep-0604/)
- [PEP 585 - Built-in Generic Types](https://peps.python.org/pep-0585/)
- [PEP 563 - Postponed Evaluation](https://peps.python.org/pep-0563/)
- [What's New in Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)
