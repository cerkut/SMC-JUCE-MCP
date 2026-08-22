---
name: juce-build-release
description: Guide JUCE-Plugin-Starter build, test, sign, notarize, package, publish, and release workflows across macOS, Windows, and Linux. Use when a project needs help choosing `scripts/build.sh` or `scripts/build.ps1` targets and actions, deciding whether to regenerate CMake, running Catch2 or PluginVal tests, exporting signing secrets, or updating website download links after a release.
---

# JUCE Build and Release

Use this skill for the portable workflow behind `/juce-dev:build`.

## Start Here

1. Inspect the project first:
   - `python3 ../../shared/scripts/inspect_juce_project.py`
2. If you want a direct portable wrapper, use:
   - `python3 ../../shared/scripts/build_release.py`
2. Confirm the repo is a JUCE-Plugin-Starter project.
3. Prefer the project's own scripts over ad-hoc `cmake` or `xcodebuild` commands:
   - macOS/Linux: `scripts/build.sh`
   - Windows: `scripts/build.ps1`

## Target and Action Mapping

Targets:
- `all`
- `au`
- `auv3`
- `vst3`
- `clap`
- `standalone`

Actions:
- `local`
- `test`
- `sign`
- `notarize`
- `pkg`
- `publish`
- `unsigned`
- `uninstall`

Examples:
- local dev build: `./scripts/build.sh standalone`
- test pass: `./scripts/build.sh all test`
- macOS publish: `./scripts/build.sh all publish`
- Windows publish: `./scripts/build.ps1 all publish`

## Workflow

1. Read `.env` and confirm project identity, formats, version, and signing settings.
2. Check the requested platform and pick the right script.
3. Before `publish` or `uninstall`, confirm the user intends a destructive or public action.
4. If the build graph looks stale, regenerate first:
   - macOS: `./scripts/generate_and_open_xcode.sh`
   - otherwise rely on `build.sh` or `build.ps1`
5. For `test`, report both unit-test and validation results if the project runs them.
6. For `publish`, also check:
   - `GITHUB_USER` and `GITHUB_REPO`
   - Apple signing values on macOS
   - CI secret export path if the user wants GitHub Actions parity
7. If the repo has `scripts/update_download_links.sh`, use it after a successful release or when the user wants website buttons updated.

## Secret and Release Helpers

If the user wants CI signing parity, prefer the project's helper scripts:
- `scripts/export_signing_certs.sh`
- `scripts/update_download_links.sh`

Use them instead of hand-rolling `gh secret set` or README link edits.

## Toolkit Wrapper

`../../shared/scripts/build_release.py` wraps the starter build scripts and adds:
- portable project-root targeting
- target and action parsing
- basic CMake regeneration detection
- a dry-run mode so the agent can show the exact command before running it

## Guardrails

- Do not invent a `draft` build action. The plugin README mentions draft flows, but the project build script and command spec center on `publish`, `pkg`, `unsigned`, and related actions.
- If the repo is not a JUCE-Plugin-Starter project, say so clearly and fall back to the project's own build instructions.
- If the request is really about Visage integration, switch to `juce-setup-visage` or `juce-visage-ui`.
- If the request is really about CI or website operations, use the dedicated toolkit skills once available instead of cramming those steps into the build flow.
