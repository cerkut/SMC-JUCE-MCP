#!/usr/bin/env bash
# Validate a built plugin with Tracktion's pluginval.
#
# Usage:
#   scripts/run_pluginval.sh <path-to-plugin> [strictness-level] [extra pluginval args...]
#
# <path-to-plugin> is a built VST3/AU/CLAP bundle from a generated plugin's
# build dir, e.g.:
#   ../pesto-pitch-tracker/build/PestoPitchTracker_artefacts/Release/VST3/PestoPitchTracker.vst3
#
# strictness-level defaults to 10 (max). See:
# https://github.com/Tracktion/pluginval#strictness-level
#
# Downloads a pinned pluginval release into .pluginval-cache/ on first run
# (cached across invocations) if no `pluginval` binary is already on PATH.
set -euo pipefail

PLUGINVAL_VERSION="${PLUGINVAL_VERSION:-1.0.4}"
CACHE_DIR="${PLUGINVAL_CACHE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.pluginval-cache}"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <path-to-plugin> [strictness-level] [extra pluginval args...]" >&2
    exit 1
fi

PLUGIN_PATH="$1"
shift
STRICTNESS="${1:-10}"
if [ $# -ge 1 ]; then shift; fi

if [ ! -e "$PLUGIN_PATH" ]; then
    echo "error: plugin not found at $PLUGIN_PATH" >&2
    exit 1
fi

resolve_pluginval_binary() {
    if command -v pluginval >/dev/null 2>&1; then
        command -v pluginval
        return
    fi

    local os
    os="$(uname -s)"
    local archive_name bin_path
    case "$os" in
        Darwin)
            archive_name="pluginval_macOS.zip"
            bin_path="$CACHE_DIR/pluginval.app/Contents/MacOS/pluginval"
            ;;
        Linux)
            archive_name="pluginval_Linux.zip"
            bin_path="$CACHE_DIR/pluginval"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            archive_name="pluginval_Windows.zip"
            bin_path="$CACHE_DIR/pluginval.exe"
            ;;
        *)
            echo "error: unsupported OS '$os' for auto-download; install pluginval manually and put it on PATH" >&2
            exit 1
            ;;
    esac

    if [ -x "$bin_path" ]; then
        echo "$bin_path"
        return
    fi

    mkdir -p "$CACHE_DIR"
    local url="https://github.com/Tracktion/pluginval/releases/download/v${PLUGINVAL_VERSION}/${archive_name}"
    echo "Downloading pluginval v${PLUGINVAL_VERSION} to $CACHE_DIR ..." >&2
    curl -fsSL -o "$CACHE_DIR/$archive_name" "$url"
    (cd "$CACHE_DIR" && unzip -oq "$archive_name")
    chmod +x "$bin_path" 2>/dev/null || true

    if [ ! -x "$bin_path" ]; then
        echo "error: pluginval binary not found at $bin_path after extraction" >&2
        exit 1
    fi
    echo "$bin_path"
}

PLUGINVAL_BIN="$(resolve_pluginval_binary)"

echo "Running pluginval (strictness $STRICTNESS) on: $PLUGIN_PATH"
"$PLUGINVAL_BIN" --strictness-level "$STRICTNESS" --validate "$PLUGIN_PATH" "$@"
