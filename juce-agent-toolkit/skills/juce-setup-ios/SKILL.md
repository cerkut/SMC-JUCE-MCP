---
name: juce-setup-ios
description: "Add or repair an iOS or iPadOS app target in a JUCE-Plugin-Starter project. Use when a project needs the portable equivalent of `setup-ios`: deciding between plain JUCE and Visage modes, creating app entrypoint files, wiring the CMake app target, and validating safe-area, touch, and simulator/device build details."
---

# JUCE Setup iOS

Use this skill for the portable workflow behind `/juce-dev:setup-ios`.

## Start Here

1. Inspect the project first:
   - `python3 ../../shared/scripts/inspect_juce_project.py`
2. Confirm the repo is a JUCE-Plugin-Starter project.
3. Detect whether the project is in:
   - plain JUCE mode
   - Visage mode

Visage mode usually means:
- `USE_VISAGE_UI=TRUE`
- `external/visage/` exists
- the desktop UI already uses the Visage bridge

## Setup Goal

The target result is an app target that shares the existing project codebase while adding:
- an iOS app entrypoint
- a main component or bridge component appropriate for the project
- CMake wiring for the app target
- safe-area aware layout
- touch-first interaction assumptions

## Preferred Workflow

1. Reuse the project's existing editor or bridge patterns instead of inventing a separate UI architecture.
2. For plain JUCE projects:
   - create a standard `JUCEApplication` entrypoint
   - add a `MainComponent`
   - keep layout straightforward and touch-friendly
3. For Visage projects:
   - reuse the existing bridge approach
   - keep mouse forwarding disabled on iOS
   - let Visage's Metal view handle touch events natively
4. Add or update the CMake app target in a way that does not break the plugin targets.
5. Validate simulator build first, then device-signing flow.

## What to Verify

- the project still builds for its desktop plugin targets
- the iOS app target builds separately
- safe-area insets are respected
- touch targets are usable
- Visage projects follow the `juce-visage-ui` iOS guidance after setup

## Handoff

Use `juce-visage-ui` after setup if the app is Visage-based. That skill holds the detailed iOS touch, Metal, and safe-area integration guidance.

## Guardrails

- There is no single reusable starter script for this flow today. Expect targeted file edits instead of a one-command setup script.
- Do not assume the plugin editor can be dropped into an iOS app untouched.
- Prefer minimal, explicit app-target wiring over large structural refactors.
