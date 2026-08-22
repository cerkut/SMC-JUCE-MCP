---
name: juce-ci-release
description: "Guide portable CI and release operations for JUCE-Plugin-Starter projects. Use when an agent needs the closest cross-host equivalent of `/juce-dev:ci`: checking workflow presence, verifying GitHub CLI/auth, exporting signing secrets, preparing release notes, or dispatching and inspecting GitHub Actions runs."
---

# JUCE CI Release

Use this skill for the portable workflow behind `/juce-dev:ci`.

## Start Here

1. Inspect the project:
   - `python3 ../../shared/scripts/inspect_juce_project.py`
2. Verify:
   - `.github/workflows/build.yml` exists
   - `gh` is installed and authenticated
   - the repo has an `origin` remote
3. If the user wants signing parity, prefer the project's existing secret export helper:
   - `scripts/export_signing_certs.sh`

## Release Helpers

The toolkit ships portable release helpers in `../../shared/scripts/`:
- `bump_version.py`
- `generate_release_notes.py`

Use them when the project does not already ship equivalent versions, or when you need a predictable release-notes baseline.

## Workflow

1. Confirm whether the user wants:
   - status
   - logs
   - secrets
   - trigger build
   - trigger publish
2. Use `gh run list`, `gh run view`, and `gh workflow run` directly when the repo is already wired for GitHub Actions.
3. Keep secret handling explicit. Verify names and presence before pushing anything.
4. For publish flows, coordinate with `juce-build-release` and `juce-auto-updates` if the project ships installers or appcasts.

## Guardrails

- This skill does not replace the Claude plugin's interactive CI menuing.
- Avoid inventing workflow inputs the project does not actually support.
- If `build.yml` is missing, say so clearly and treat CI setup as a repo-scaffolding task, not a trigger task.
