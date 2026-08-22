---
name: juce-auto-updates
description: Add, validate, or repair auto-update support in a JUCE-Plugin-Starter project. Use when a project needs Sparkle or WinSparkle setup, EdDSA key guidance, feed URL wiring, updater-related source and CMake checks, or a doctor pass similar to `/juce-dev:setup-updates --doctor`.
---

# JUCE Auto Updates

Use this skill for the portable workflow behind `/juce-dev:setup-updates`.

## Start Here

1. Inspect the project first:
   - `python3 ../../shared/scripts/inspect_juce_project.py`
2. Use the portable wrapper when you want the toolkit to run the setup flow:
   - `python3 ../../shared/scripts/setup_updates.py --doctor --generate-appcasts`
2. Run the updater doctor before making changes:
   - `python3 ../../shared/scripts/auto_update_doctor.py`
3. Confirm whether the goal is:
   - first-time setup
   - repair
   - validation only

## Setup Workflow

Prefer the project's own scripts when they exist:
- `scripts/setup_sparkle.sh`
- `scripts/setup_winsparkle.sh`

If the project does not already include them, the toolkit also ships portable copies:
- `../../shared/scripts/setup_sparkle.sh`
- `../../shared/scripts/setup_winsparkle.sh`

Typical flow:
1. Download Sparkle for macOS and WinSparkle for Windows as needed.
2. Confirm the framework or library files landed in `external/`.
3. Ensure `.env` has:
   - `ENABLE_AUTO_UPDATE=TRUE`
   - `AUTO_UPDATE_MODE`
   - `AUTO_UPDATE_EDDSA_PUBLIC_KEY`
   - feed URLs for the platforms you ship
4. Verify the source files and CMake wiring are present.
5. Run the doctor again and report what is still missing.

## Toolkit Wrapper

`../../shared/scripts/setup_updates.py` can:
- download Sparkle or WinSparkle
- set the core updater env keys
- generate appcast placeholder files
- run the doctor immediately after setup

## Doctor Script

Use `../../shared/scripts/auto_update_doctor.py` for a repeatable validation pass. It checks:
- `.env` updater keys
- Sparkle and WinSparkle download state
- updater source files
- CMake wiring
- feed URLs
- appcast XML presence and basic validity

## Guardrails

- Do not claim Linux updater parity unless the project actually ships a Linux updater implementation.
- Keep the private EdDSA key out of the repo. Only the public key belongs in `.env`.
- First-time setup is not complete until the doctor script is mostly clean and the app menu path is verified in a built app.
