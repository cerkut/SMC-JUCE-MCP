#!/bin/bash

set -euo pipefail

ROOT_DIR="$(pwd)"
EXTERNAL_DIR="$ROOT_DIR/external"
WINSPARKLE_DIR="$EXTERNAL_DIR/WinSparkle"
WINSPARKLE_VERSION="${WINSPARKLE_VERSION:-0.9.2}"
WINSPARKLE_URL="https://github.com/vslavik/winsparkle/releases/download/v${WINSPARKLE_VERSION}/WinSparkle-${WINSPARKLE_VERSION}.zip"

echo "=== Setting up WinSparkle $WINSPARKLE_VERSION ==="

if [[ -f "$WINSPARKLE_DIR/include/winsparkle.h" ]]; then
    echo "WinSparkle already present at $WINSPARKLE_DIR"
    exit 0
fi

TEMP_DIR="$(mktemp -d)"
trap "rm -rf '$TEMP_DIR'" EXIT
ARCHIVE="$TEMP_DIR/WinSparkle.zip"

mkdir -p "$EXTERNAL_DIR"
curl -fSL "$WINSPARKLE_URL" -o "$ARCHIVE"
cd "$TEMP_DIR"
unzip -q "$ARCHIVE"

EXTRACTED_DIR="$TEMP_DIR/WinSparkle-${WINSPARKLE_VERSION}"
if [[ ! -d "$EXTRACTED_DIR" ]]; then
    echo "Error: extracted WinSparkle directory not found"
    exit 1
fi

rm -rf "$WINSPARKLE_DIR"
mkdir -p "$WINSPARKLE_DIR"
cp -R "$EXTRACTED_DIR/include" "$WINSPARKLE_DIR/"

if [[ -d "$EXTRACTED_DIR/x64/Release" ]]; then
    mkdir -p "$WINSPARKLE_DIR/x64"
    cp "$EXTRACTED_DIR/x64/Release/WinSparkle.dll" "$WINSPARKLE_DIR/x64/"
    cp "$EXTRACTED_DIR/x64/Release/WinSparkle.lib" "$WINSPARKLE_DIR/x64/"
fi

if [[ -d "$EXTRACTED_DIR/ARM64/Release" ]]; then
    mkdir -p "$WINSPARKLE_DIR/arm64"
    cp "$EXTRACTED_DIR/ARM64/Release/WinSparkle.dll" "$WINSPARKLE_DIR/arm64/"
    cp "$EXTRACTED_DIR/ARM64/Release/WinSparkle.lib" "$WINSPARKLE_DIR/arm64/"
fi

if [[ -d "$EXTRACTED_DIR/bin" ]]; then
    cp -R "$EXTRACTED_DIR/bin" "$WINSPARKLE_DIR/"
fi

if [[ -f "$EXTRACTED_DIR/COPYING" ]]; then
    cp "$EXTRACTED_DIR/COPYING" "$WINSPARKLE_DIR/"
fi

echo "WinSparkle setup complete"
echo "  Root: $WINSPARKLE_DIR"
echo "  Tool: $WINSPARKLE_DIR/bin/winsparkle-tool.exe"
