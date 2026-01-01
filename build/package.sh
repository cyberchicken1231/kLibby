#!/bin/bash
# Package kLibby for Kindle deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build/output"
PACKAGE_NAME="klibby"
VERSION="0.1.0"

echo "Building kLibby package..."

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME"

# Copy source files
echo "Copying source files..."
cp -r "$PROJECT_DIR/src" "$BUILD_DIR/$PACKAGE_NAME/"
cp "$PROJECT_DIR/README.md" "$BUILD_DIR/$PACKAGE_NAME/"
cp "$PROJECT_DIR/LICENSE" "$BUILD_DIR/$PACKAGE_NAME/"

# Create launcher script
echo "Creating launcher script..."
cat > "$BUILD_DIR/$PACKAGE_NAME/klibby.sh" << 'EOF'
#!/bin/sh
# kLibby launcher script for Kindle

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Set up environment
export TERM=linux
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Run kLibby
exec python3 "$SCRIPT_DIR/src/main.py" "$@"
EOF

chmod +x "$BUILD_DIR/$PACKAGE_NAME/klibby.sh"

# Create installation script
echo "Creating install script..."
cat > "$BUILD_DIR/$PACKAGE_NAME/install.sh" << 'EOF'
#!/bin/sh
# kLibby installation script for Kindle

set -e

echo "Installing kLibby..."

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is not installed on this Kindle."
    echo "Please install Python first. See INSTALL.md for instructions."
    exit 1
fi

# Create installation directory
INSTALL_DIR="/mnt/us/klibby"
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying files to $INSTALL_DIR..."
cp -r src "$INSTALL_DIR/"
cp klibby.sh "$INSTALL_DIR/"
cp README.md "$INSTALL_DIR/"
cp LICENSE "$INSTALL_DIR/"

# Make launcher executable
chmod +x "$INSTALL_DIR/klibby.sh"

# Create symlink in PATH (optional)
if [ -d "/mnt/us/bin" ]; then
    ln -sf "$INSTALL_DIR/klibby.sh" /mnt/us/bin/klibby
    echo "Created symlink: /mnt/us/bin/klibby"
fi

echo ""
echo "Installation complete!"
echo ""
echo "To run kLibby:"
echo "  cd $INSTALL_DIR"
echo "  ./klibby.sh"
echo ""
echo "Or if /mnt/us/bin is in your PATH:"
echo "  klibby"
echo ""
EOF

chmod +x "$BUILD_DIR/$PACKAGE_NAME/install.sh"

# Create tarball
echo "Creating package..."
cd "$BUILD_DIR"
tar -czf "$PROJECT_DIR/klibby-$VERSION.tar.gz" "$PACKAGE_NAME"

echo ""
echo "Package created: klibby-$VERSION.tar.gz"
echo ""
echo "To install on Kindle:"
echo "  1. Copy klibby-$VERSION.tar.gz to your Kindle"
echo "  2. Extract: tar -xzf klibby-$VERSION.tar.gz"
echo "  3. Run: cd klibby && ./install.sh"
echo ""
