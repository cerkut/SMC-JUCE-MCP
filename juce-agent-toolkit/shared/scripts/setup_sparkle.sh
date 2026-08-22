#!/bin/bash

set -euo pipefail

ROOT_DIR="$(pwd)"
EXTERNAL_DIR="$ROOT_DIR/external"
SPARKLE_VERSION="${SPARKLE_VERSION:-2.8.0}"
SPARKLE_FRAMEWORK="$EXTERNAL_DIR/Sparkle.framework"

echo "=== Setting up Sparkle $SPARKLE_VERSION ==="

if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: Sparkle is macOS-only. Current platform: $(uname)"
    exit 1
fi

if [[ -d "$SPARKLE_FRAMEWORK" ]]; then
    echo "Sparkle framework already present at $SPARKLE_FRAMEWORK"
    exit 0
fi

mkdir -p "$EXTERNAL_DIR"

SPARKLE_URL="https://github.com/sparkle-project/Sparkle/releases/download/$SPARKLE_VERSION/Sparkle-$SPARKLE_VERSION.tar.xz"
DOWNLOAD_FILE="$EXTERNAL_DIR/sparkle-$SPARKLE_VERSION.tar.xz"

curl -fSL "$SPARKLE_URL" -o "$DOWNLOAD_FILE"
cd "$EXTERNAL_DIR"
rm -rf Sparkle.framework bin Symbols sparkle.app "Sparkle Test App.app" CHANGELOG INSTALL LICENSE SampleAppcast.xml
tar -xf "sparkle-$SPARKLE_VERSION.tar.xz"
rm -f "sparkle-$SPARKLE_VERSION.tar.xz"

if [[ ! -d "$SPARKLE_FRAMEWORK" ]]; then
    echo "Error: Sparkle.framework not found after extraction"
    exit 1
fi

echo "Sparkle setup complete"
echo "  Framework: $SPARKLE_FRAMEWORK"
echo "  sign_update: $EXTERNAL_DIR/bin/sign_update"
echo "  generate_keys: $EXTERNAL_DIR/bin/generate_keys"
