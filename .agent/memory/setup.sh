#!/bin/bash
# Setup the project memory system — creates a local venv and installs dependencies.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
    echo "Venv already exists at $VENV_DIR"
else
    echo "Creating venv..."
    python3 -m venv "$VENV_DIR"
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "Done. Run the memory system with:"
echo "  $VENV_DIR/bin/python $SCRIPT_DIR/project-memory inspect help"
echo ""
echo "Or add this alias to your shell:"
echo "  alias pmem='$VENV_DIR/bin/python $SCRIPT_DIR/project-memory'"
