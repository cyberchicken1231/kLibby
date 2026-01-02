#!/bin/sh
# kLibby launcher script for Kindle

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Set up environment
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Run kLibby with simple text interface (no curses)
cd "$SCRIPT_DIR/src"
python3 << 'PYTHON_EOF'
import ssl

# Disable SSL verification (Kindle has outdated CA certificates)
ssl._create_default_https_context = ssl._create_unverified_context

# Import and run simple text-based interface
import main_simple
main_simple.main()
PYTHON_EOF
