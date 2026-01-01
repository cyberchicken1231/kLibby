# Contributing to kLibby

Thank you for your interest in contributing to kLibby! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Bugs

Found a bug? Please open an issue with:

1. **Clear title** describing the bug
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - Kindle model
   - Firmware version
   - Python version
   - kLibby version

### Suggesting Features

Have an idea? Open an issue with:

1. **Use case** - Why is this needed?
2. **Proposed solution** - How should it work?
3. **Alternatives** - Other approaches you considered
4. **Priority** - Nice to have vs. essential

### Code Contributions

1. **Fork** the repository
2. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test** on actual Kindle hardware if possible
5. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.7+
- Git
- (Optional) Kindle device for testing

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/kLibby.git
cd kLibby

# Run locally
python3 src/main.py
```

### Testing on Desktop

kLibby works in any terminal:

```bash
# Just run it!
python3 src/main.py
```

Use your actual Libby credentials to test functionality.

### Testing on Kindle

```bash
# Build package
./build/package.sh

# Transfer to Kindle
scp klibby-0.1.0.tar.gz root@kindle:/mnt/us/

# On Kindle, install and test
ssh root@kindle
cd /mnt/us
tar -xzf klibby-0.1.0.tar.gz
cd klibby
./install.sh
klibby
```

## Code Style

### Python Style

Follow PEP 8 with these specifics:

- **Indentation**: 4 spaces
- **Line length**: 100 characters max
- **Docstrings**: Google style
- **Type hints**: Encouraged but not required

Example:
```python
def download_book(
    self,
    card_id: str,
    loan_id: str,
    output_path: str
) -> str:
    """
    Download a book to file

    Args:
        card_id: Library card ID
        loan_id: Loan ID
        output_path: Path to save file

    Returns:
        Path to downloaded file

    Raises:
        Exception: If download fails
    """
    # Implementation here
    pass
```

### Code Organization

- **`src/libby/`** - Libby API client
- **`src/ui/`** - User interface
- **`src/utils/`** - Utility functions
- **`build/`** - Build scripts
- **`docs/`** - Documentation

### Comments

- Use comments sparingly
- Prefer self-documenting code
- Comment "why" not "what"
- Docstrings for all public functions/classes

## Areas for Contribution

### High Priority

1. **Search/Browse** functionality
   - Search library catalog
   - Browse categories
   - Filter by format/availability

2. **Audiobook support**
   - Download audiobooks
   - Basic playback (if feasible)

3. **Better error handling**
   - More informative error messages
   - Retry logic for network failures
   - Graceful degradation

### Medium Priority

1. **Reading interface** (integrated reader)
2. **Book metadata** display
3. **Series grouping**
4. **Reading statistics**
5. **Recommendations**

### Low Priority

1. **UI themes/customization**
2. **Localization** (multiple languages)
3. **Cloud sync** for settings
4. **Social features** (share recommendations)

## Technical Guidelines

### Dependencies

- **Minimize external dependencies**
- Use Python standard library when possible
- Document why external deps are needed
- Ensure deps work on ARMv7

### Performance

- **Optimize for e-ink**: Minimize screen refreshes
- **Memory conscious**: Kindle has limited RAM
- **Async operations**: Don't block UI
- **Cache wisely**: Balance speed vs. storage

### Security

- **Never log** auth tokens or passwords
- **Secure storage** of credentials
- **HTTPS only** for API calls
- **Validate inputs** from user and API

### Compatibility

Test on:
- ✅ Kindle Paperwhite Gen 11 (primary target)
- ⚠️ Other Kindle models (nice to have)
- ℹ️ Desktop (for development)

## Pull Request Process

### Before Submitting

1. **Test thoroughly** on Kindle if possible
2. **Update documentation** if needed
3. **Add tests** if applicable
4. **Follow code style** guidelines

### PR Description

Include:

1. **What** - What does this PR do?
2. **Why** - Why is this change needed?
3. **How** - How was it implemented?
4. **Testing** - How was it tested?
5. **Screenshots** (for UI changes)

Example:
```markdown
## What
Adds search functionality to browse library catalog

## Why
Users requested ability to search for books directly from Kindle

## How
- Added new `search()` method to LibbyClient
- Created search UI in MenuUI
- Integrated with main menu

## Testing
- Tested on Kindle Paperwhite Gen 11
- Verified searches work for title, author, ISBN
- Confirmed results display correctly

## Screenshots
[Screenshot of search interface]
```

### Review Process

1. **Automated checks** run automatically
2. **Maintainer review** - we'll review your code
3. **Feedback** - address any comments
4. **Merge** - once approved, we'll merge!

## Code Review Guidelines

When reviewing others' PRs:

- Be kind and constructive
- Suggest improvements, don't demand
- Explain the "why" behind suggestions
- Approve if code is good enough (perfect is enemy of good)

## Documentation

### Updating Docs

If your change affects:

- **User-facing features** → Update USAGE.md
- **Installation** → Update INSTALL.md
- **API** → Update docstrings + README
- **Building** → Update build/README.md

### Writing Style

- Clear and concise
- Assume reader is technical but new to project
- Use examples liberally
- Link to related docs

## Community

### Communication

- **GitHub Issues** - Bug reports, features
- **Pull Requests** - Code contributions
- **MobileRead Forums** - General discussion
- **Email** - Security issues only

### Code of Conduct

Be respectful and professional:

- ✅ Respectful disagreement
- ✅ Constructive criticism
- ✅ Help others learn
- ❌ Personal attacks
- ❌ Harassment
- ❌ Spam

## Legal

### License

By contributing, you agree that your contributions will be licensed under the MIT License.

### Copyright

- Retain original copyright headers
- Add your name to contributors list
- Don't remove others' attributions

### Attribution

kLibby builds on work by:
- [odmpy](https://github.com/ping/odmpy) - Libby API reference
- [libby-calibre-plugin](https://github.com/ping/libby-calibre-plugin) - API implementation

Please maintain these attributions.

## Getting Help

### For Contributors

- **Technical questions** - Open a discussion on GitHub
- **Code help** - Comment on your PR
- **General** - MobileRead forums

### Resources

- [Libby API unofficial docs](https://github.com/ping/odmpy)
- [Kindle hacking wiki](https://wiki.mobileread.com/wiki/Kindle_Hacking)
- [Python curses tutorial](https://docs.python.org/3/howto/curses.html)
- [MobileRead forums](https://www.mobileread.com/forums/)

## Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Appreciated forever! 🙏

## Thank You!

Every contribution helps make kLibby better. Whether it's code, documentation, bug reports, or suggestions - thank you for contributing!

Happy coding! 🚀
