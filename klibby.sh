#!/bin/sh
# kLibby launcher script for Kindle

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Set terminal type for curses
export TERM=linux
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Run kLibby with SSL fix for Kindle's outdated certificates
cd "$SCRIPT_DIR/src"
python3 << 'PYTHON_EOF'
import ssl
import os

# Disable SSL verification (Kindle has outdated CA certificates)
ssl._create_default_https_context = ssl._create_unverified_context

# Ensure TERM is set
os.environ['TERM'] = 'linux'

# Import and run main
import main
main.main()
PYTHON_EOF
