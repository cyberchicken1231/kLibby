# kLibby Tests

Test suite for kLibby (coming soon).

## Running Tests

Currently, kLibby has limited automated tests. Manual testing on actual Kindle hardware is recommended.

### Manual Testing Checklist

Before each release, verify:

- [ ] Authentication via sync code works
- [ ] Loans display correctly
- [ ] Holds display correctly
- [ ] Library cards display correctly
- [ ] Book download works (ePub)
- [ ] Book download works (ACSM when DRM)
- [ ] Return loan early works
- [ ] Navigation (all menu items accessible)
- [ ] Back/quit functions work
- [ ] Settings → Clear auth works
- [ ] Re-authentication after clearing works

### Test Environments

1. **Desktop** (development):
   ```bash
   python3 src/main.py
   ```

2. **Kindle Paperwhite Gen 11** (target):
   ```bash
   ssh root@kindle
   cd /mnt/us/klibby
   ./klibby.sh
   ```

## Future: Automated Tests

Planned test coverage:

### Unit Tests

- LibbyClient API methods
- Model parsing (Loan, Hold, Card)
- MenuUI components
- Error handling

### Integration Tests

- Full auth flow
- Download flow
- Return flow
- Settings management

### Example Test Structure

```python
# tests/test_libby_client.py

import unittest
from libby.client import LibbyClient
from libby.models import Card, Loan

class TestLibbyClient(unittest.TestCase):
    def test_get_chip(self):
        """Test getting anonymous identity chip"""
        client = LibbyClient()
        chip = client.get_chip()
        self.assertIn('identity', chip)

    def test_sync_unauthenticated(self):
        """Test sync fails when not authenticated"""
        client = LibbyClient()
        with self.assertRaises(Exception):
            client.sync()

# More tests to come...
```

## Contributing Tests

See CONTRIBUTING.md for guidelines on adding tests.

## Test Data

**DO NOT commit**:
- Real auth tokens
- Real library card numbers
- Personal information

Use mock data or test libraries only.
