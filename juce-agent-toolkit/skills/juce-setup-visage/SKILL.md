---
name: juce-setup-visage
description: Add or repair Visage GPU UI setup in an existing JUCE-Plugin-Starter project. Use when a project needs the `setup_visage.sh` workflow, Visage template files copied into place, `USE_VISAGE_UI=TRUE` enabled, CMake wired up, or a clean handoff into the `juce-visage-ui` skill for deeper UI work.
---

# JUCE Setup Visage

Use this skill for the portable workflow behind `/juce-dev:setup-visage`.

## Start Here

1. Inspect the project first:
   - `python3 ../../shared/scripts/inspect_juce_project.py`
2. Confirm the repo is a JUCE-Plugin-Starter project.
3. Check whether Visage is already enabled:
   - `.env` contains `USE_VISAGE_UI=TRUE`
   - `external/visage/` exists
   - `Source/Visage/` exists

If all of those are already in place, switch to `juce-visage-ui` for implementation or debugging instead of re-running setup.

## Preferred Setup Path

Prefer the project's own Visage setup assets:
- `templates/visage/PluginEditor.h`
- `templates/visage/PluginEditor.cpp`
- `scripts/setup_visage.sh`

Workflow:
1. Detect the project class name from `Source/PluginEditor.h` and related source files.
2. If the Visage editor templates exist, copy them into the project and replace `CLASS_NAME_PLACEHOLDER`.
3. Run `scripts/setup_visage.sh`.
4. Verify `.env` now contains `USE_VISAGE_UI=TRUE`.
5. Rebuild and confirm the project still compiles.

## What to Verify After Setup

- `external/visage/` exists
- the Visage bridge files were copied into `Source/Visage/`
- `CMakeLists.txt` contains the Visage block
- `.env` enables Visage
- the editor follows the native-title-bar sizing pattern if the template uses it

## Handoff

Once setup is complete, use `juce-visage-ui` for:
- bridge behavior
- keyboard and focus issues in DAWs
- popup and modal behavior
- iOS touch handling
- rendering or destruction-order bugs

## Guardrails

- Prefer the repo's `setup_visage.sh` over manual edits when it exists.
- If the project is not starter-based, explain that this skill assumes the starter's template structure and then apply only the minimal manual Visage wiring the project actually needs.
- Do not rewrite the whole editor if the repo already has a custom Visage bridge. Repair the existing integration instead.
