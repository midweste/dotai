#!/usr/bin/env bash
# Install: bash -c "$(curl -fsSL https://raw.githubusercontent.com/midweste/dotai/main/AGENTS.sh)"
# Update: bash ./AGENTS.sh
set -euo pipefail

command -v git >/dev/null 2>&1 || { echo "Error: git not found." >&2; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo "Error: rsync not found." >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR"

REPO_URL="git@github.com:midweste/dotai.git"
REFERENCE="main"

temp_dir="$(mktemp -d)"
cleanup() {
    rm -rf "$temp_dir"
}
trap cleanup EXIT

printf 'Fetching %s (%s)\n' "$REPO_URL" "$REFERENCE"
git clone --depth 1 --branch "$REFERENCE" "$REPO_URL" "$temp_dir/src" >/dev/null 2>&1 || {
    echo "Error: git clone failed" >&2
    exit 1
}

rsync -av \
    --exclude '.git' \
    --exclude '.github' \
    --exclude '.gitmodules' \
    "$temp_dir/src/" "$TARGET_DIR/"

echo 'Policy files synchronized. Review changes and commit as needed.'
