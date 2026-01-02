#!/bin/sh
# kLibby launcher script for Kindle

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Set up environment
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Run the wrapper script (avoids stdin issues with heredoc)
cd "$SCRIPT_DIR/src"
python3 run_simple.py
